#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <dlfcn.h>
#include <dirent.h>
#include <limits.h>
#include <unistd.h>
#include <time.h>
#include "lance_runtime_probe/duckdb.h"
#include "ort_drive_run/onnxruntime_c_api.h"
#include <math.h>

static void *kernel_handle=NULL, *omni_handle=NULL;
static float (*native_dot)(const float*,const float*,size_t)=NULL;
static int (*omni_models)(void)=NULL, (*omni_lanes)(void)=NULL;
static void *live_libs[128]; static int lib_count=0;
static void json_escape(const char *s, char *out,size_t cap) {size_t j=0; for(size_t i=0;s[i]&&j+5<cap;i++){unsigned char c=s[i];if(c=='"'||c=='\\'){out[j++]='\\';out[j++]=c;}else if(c=='\n'){out[j++]='\\';out[j++]='n';}else if(c>=32){out[j++]=c;}}out[j]=0;}
static void run(duckdb_connection con,const char *label,const char *sql,int maxrows){
 duckdb_result r; memset(&r,0,sizeof(r)); duckdb_state state=duckdb_query(con,sql,&r);
 char elabel[256];json_escape(label,elabel,sizeof(elabel));
 if(state!=DuckDBSuccess){char e[2000];json_escape(duckdb_result_error(&r),e,sizeof(e));printf("{\"stage\":\"%s\",\"ok\":false,\"error\":\"%s\"}\n",elabel,e);duckdb_destroy_result(&r);return;}
 printf("{\"stage\":\"%s\",\"ok\":true,\"rows\":%llu,\"data\":[",elabel,(unsigned long long)duckdb_row_count(&r));
 idx_t n=duckdb_row_count(&r),cols=duckdb_column_count(&r);for(idx_t i=0;i<n&&i<(idx_t)maxrows;i++){if(i)printf(",");printf("[");for(idx_t j=0;j<cols;j++){if(j)printf(",");char *v=duckdb_value_varchar(&r,j,i);if(!v){printf("null");continue;}char buf[7000];json_escape(v,buf,sizeof(buf));printf("\"%s\"",buf);duckdb_free(v);}printf("]");}printf("]}\n");duckdb_destroy_result(&r);
}
static const OrtApi *onnx_api=NULL; static OrtEnv *onnx_env=NULL; static OrtSessionOptions *onnx_options=NULL;static OrtMemoryInfo *onnx_mem=NULL;
typedef struct {OrtSession *session;char name[100];char filename[150];} OnnxActor;
static OnnxActor model_actors[4]; static int model_count=0;
static int ortcheck(OrtStatus *s,const char *stage){if(!s)return 1;char buf[1200];json_escape(onnx_api->GetErrorMessage(s),buf,sizeof(buf));printf("{\"stage\":\"%s\",\"ok\":false,\"error\":\"%s\"}\n",stage,buf);onnx_api->ReleaseStatus(s);return 0;}
static int setup_onnx(const char *root){
 const OrtApiBase *base=OrtGetApiBase();if(!base){printf("{\"stage\":\"ort_base\",\"ok\":false}\n");return 0;}
 onnx_api=base->GetApi(ORT_API_VERSION);if(!onnx_api)return 0;
 if(!ortcheck(onnx_api->CreateEnv(ORT_LOGGING_LEVEL_ERROR,"room9_duckdb",&onnx_env),"ort_env"))return 0;
 if(!ortcheck(onnx_api->CreateSessionOptions(&onnx_options),"ort_options"))return 0;
 ortcheck(onnx_api->SetIntraOpNumThreads(onnx_options,1),"ort_threads");
 if(!ortcheck(onnx_api->CreateCpuMemoryInfo(OrtArenaAllocator,OrtMemTypeDefault,&onnx_mem),"ort_mem"))return 0;
 const char *models[]={"sovereign_projection_head.onnx.bin","sovereign_latent_steerer.onnx.bin","sovereign_latent_decoder.onnx.bin","sovereign_quantum_rotator.onnx.bin"};
 const char *names[]={"sovereign_onnx_projection_first","sovereign_onnx_steerer_first","sovereign_onnx_decoder_first","sovereign_onnx_rotator_first"};
 for(int i=0;i<4;i++){char path[PATH_MAX];snprintf(path,sizeof(path),"%s/%s",root,models[i]);OrtSession*session=NULL;char stage[150];snprintf(stage,sizeof(stage),"ort_session_%d",i);
   if(ortcheck(onnx_api->CreateSession(onnx_env,path,onnx_options,&session),stage)){
     OnnxActor *m=&model_actors[model_count++];m->session=session;snprintf(m->name,sizeof(m->name),"%s",names[i]);snprintf(m->filename,sizeof(m->filename),"%s",models[i]);
     printf("{\"stage\":\"onnx_model_load\",\"ok\":true,\"name\":\"%s\",\"runtime\":\"%s\"}\n",models[i],base->GetVersionString());
   }
 }
 return model_count;
}
static float onnx_first(const OnnxActor *model){
 size_t nin=0,nout=0;float value=NAN;OrtAllocator *allocator=NULL;OrtValue **inputs=NULL,*out=NULL;char **names=NULL,*output_name=NULL;float **data=NULL;
 if(!ortcheck(onnx_api->SessionGetInputCount(model->session,&nin),"ort_num_inputs"))goto done;
 if(!ortcheck(onnx_api->SessionGetOutputCount(model->session,&nout),"ort_num_outputs")||!nout)goto done;
 if(!ortcheck(onnx_api->GetAllocatorWithDefaultOptions(&allocator),"ort_allocator"))goto done;
 names=calloc(nin,sizeof(*names));inputs=calloc(nin,sizeof(*inputs));data=calloc(nin,sizeof(*data));
 for(size_t i=0;i<nin;i++){
   OrtTypeInfo *info=NULL;const OrtTensorTypeAndShapeInfo *tensor_info=NULL;ONNXTensorElementDataType type;size_t nd=0;int64_t dims[16];size_t count=1;
   if(!ortcheck(onnx_api->SessionGetInputName(model->session,i,allocator,&names[i]),"ort_inputname"))goto done;
   if(!ortcheck(onnx_api->SessionGetInputTypeInfo(model->session,i,&info),"ort_inputtype"))goto done;
   if(!ortcheck(onnx_api->CastTypeInfoToTensorInfo(info,&tensor_info),"ort_tensor_type")){onnx_api->ReleaseTypeInfo(info);goto done;}
   if(!ortcheck(onnx_api->GetTensorElementType(tensor_info,&type),"ort_element_type")||type!=ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT){onnx_api->ReleaseTypeInfo(info);goto done;}
   if(!ortcheck(onnx_api->GetDimensionsCount(tensor_info,&nd),"ort_dims")||nd>16){onnx_api->ReleaseTypeInfo(info);goto done;}
   if(!ortcheck(onnx_api->GetDimensions(tensor_info,dims,nd),"ort_dimvalues")){onnx_api->ReleaseTypeInfo(info);goto done;}
   for(size_t j=0;j<nd;j++){if(dims[j]<=0)dims[j]=1;count*=dims[j];}onnx_api->ReleaseTypeInfo(info);
   if(count>10000000)goto done;
   data[i]=calloc(count,sizeof(float));for(size_t j=0;j<count;j++)data[i][j]=(float)(j%13)*0.01f;
   if(!ortcheck(onnx_api->CreateTensorWithDataAsOrtValue(onnx_mem,data[i],count*sizeof(float),dims,nd,ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT,&inputs[i]),"ort_inputtensor"))goto done;
 }
 if(!ortcheck(onnx_api->SessionGetOutputName(model->session,0,allocator,&output_name),"ort_outputname"))goto done;
 if(!ortcheck(onnx_api->Run(model->session,NULL,(const char*const*)names,(const OrtValue*const*)inputs,nin,(const char*const*)&output_name,1,&out),"ort_run"))goto done;
 void *raw=NULL;if(!ortcheck(onnx_api->GetTensorMutableData(out,&raw),"ort_out"))goto done;value=((float*)raw)[0];
 done:if(out)onnx_api->ReleaseValue(out);if(output_name)onnx_api->AllocatorFree(allocator,output_name);
 if(inputs)for(size_t i=0;i<nin;i++)if(inputs[i])onnx_api->ReleaseValue(inputs[i]);
 if(names)for(size_t i=0;i<nin;i++)if(names[i])onnx_api->AllocatorFree(allocator,names[i]);
 if(data)for(size_t i=0;i<nin;i++)free(data[i]);free(names);free(inputs);free(data);return value;
}
static void udf_onnx(duckdb_function_info info,duckdb_data_chunk input,duckdb_vector output){
 idx_t n=duckdb_data_chunk_get_size(input);float *out=(float*)duckdb_vector_get_data(output);
 const OnnxActor *model=(const OnnxActor*)duckdb_scalar_function_get_extra_info(info);
 for(idx_t i=0;i<n;i++)out[i]=onnx_first(model);
}
static int register_onnx_udf(duckdb_connection con,OnnxActor *m){
 duckdb_scalar_function f=duckdb_create_scalar_function();duckdb_scalar_function_set_name(f,m->name);
 duckdb_logical_type rt=duckdb_create_logical_type(DUCKDB_TYPE_FLOAT);duckdb_scalar_function_set_return_type(f,rt);duckdb_destroy_logical_type(&rt);
 duckdb_scalar_function_set_extra_info(f,m,NULL);duckdb_scalar_function_set_function(f,udf_onnx);
 int ok=duckdb_register_scalar_function(con,f)==DuckDBSuccess;duckdb_destroy_scalar_function(&f);
 printf("{\"stage\":\"register_onnx_udf\",\"function\":\"%s\",\"ok\":%s}\n",m->name,ok?"true":"false");return ok;
}
static void udf_dot4(duckdb_function_info info,duckdb_data_chunk input,duckdb_vector output) {
 idx_t n=duckdb_data_chunk_get_size(input);float *cols[8];for(int j=0;j<8;j++){cols[j]=(float*)duckdb_vector_get_data(duckdb_data_chunk_get_vector(input,j));}
 float *out=(float*)duckdb_vector_get_data(output);for(idx_t i=0;i<n;i++){float a[4],b[4];for(int j=0;j<4;j++){a[j]=cols[j][i];b[j]=cols[j+4][i];}out[i]=native_dot(a,b,4);}
}
static void udf_models(duckdb_function_info info,duckdb_data_chunk input,duckdb_vector output){idx_t n=duckdb_data_chunk_get_size(input);int64_t *out=duckdb_vector_get_data(output);for(idx_t i=0;i<n;i++)out[i]=omni_models();}
static void udf_lanes(duckdb_function_info info,duckdb_data_chunk input,duckdb_vector output){idx_t n=duckdb_data_chunk_get_size(input);int64_t *out=duckdb_vector_get_data(output);for(idx_t i=0;i<n;i++)out[i]=omni_lanes();}
static int register_udf(duckdb_connection con,const char *name,int argc,duckdb_type type,duckdb_scalar_function_t fun){
 duckdb_scalar_function f=duckdb_create_scalar_function();duckdb_scalar_function_set_name(f,name);
 for(int i=0;i<argc;i++){duckdb_logical_type t=duckdb_create_logical_type(DUCKDB_TYPE_FLOAT);duckdb_scalar_function_add_parameter(f,t);duckdb_destroy_logical_type(&t);}
 duckdb_logical_type rt=duckdb_create_logical_type(type);duckdb_scalar_function_set_return_type(f,rt);duckdb_destroy_logical_type(&rt);duckdb_scalar_function_set_function(f,fun);
 int ok=duckdb_register_scalar_function(con,f)==DuckDBSuccess;duckdb_destroy_scalar_function(&f);printf("{\"stage\":\"register_native_udf\",\"function\":\"%s\",\"ok\":%s}\n",name,ok?"true":"false");return ok;
}
static void load_all(const char *dir){DIR *d=opendir(dir);if(!d){perror("opendir libs");return;}struct dirent *e;
 while((e=readdir(d))){size_t n=strlen(e->d_name);if(n<3||strcmp(e->d_name+n-3,".so"))continue;char file[PATH_MAX];snprintf(file,sizeof(file),"%s/%s",dir,e->d_name);void *h=dlopen(file,RTLD_NOW|RTLD_LOCAL);if(h&&lib_count<128){live_libs[lib_count++]=h; if(!strcmp(e->d_name,"libsovereign_kernel_avx2.so"))kernel_handle=h;if(!strcmp(e->d_name,"sovereign_omni_kernel.so"))omni_handle=h;}
 char name[256];json_escape(e->d_name,name,sizeof(name));if(h)printf("{\"stage\":\"dlopen\",\"library\":\"%s\",\"ok\":true}\n",name);else{char err[1000];json_escape(dlerror(),err,sizeof(err));printf("{\"stage\":\"dlopen\",\"library\":\"%s\",\"ok\":false,\"error\":\"%s\"}\n",name,err);}}
 closedir(d);native_dot=kernel_handle?dlsym(kernel_handle,"sovereign_dot_product_f32"):NULL;omni_models=omni_handle?dlsym(omni_handle,"sovereign_get_total_pydantic_models"):NULL;omni_lanes=omni_handle?dlsym(omni_handle,"sovereign_get_total_vector_lanes"):NULL;
}
static void temp_view(duckdb_connection c,const char *name,const char *path,const char *fmt){
 if(access(path,R_OK)!=0){printf("{\"stage\":\"source_missing\",\"name\":\"%s\",\"ok\":false}\n",name);return;}char q[PATH_MAX*2];snprintf(q,sizeof(q),"CREATE TEMP VIEW %s AS SELECT * FROM %s('%s')",name,!strcmp(fmt,"json")?"read_json_auto":"read_parquet",path);run(c,name,q,0);
}
int main(int argc,char**argv){const char *root=argc>1?argv[1]:"/mnt/data";const char *db=getenv("SOVEREIGN_DUCKDB_PATH");
 if(db && access(db,R_OK)!=0){fprintf(stderr,"SOVEREIGN_DUCKDB_PATH unreadable: %s\n",db);return 9;}
 char bdir[PATH_MAX];snprintf(bdir,sizeof(bdir),"%s/sovereign_inspection/sovereign_master_distribution/binaries",root);load_all(bdir);
 duckdb_database database=NULL;duckdb_connection con=NULL;if(duckdb_open(db&&*db?db:NULL,&database)!=DuckDBSuccess)return 10;if(duckdb_connect(database,&con)!=DuckDBSuccess)return 11;
 run(con,"duckdb_version","SELECT version()",1);
 const char *exts[]={"autocomplete","core_functions","icu","json","parquet","lance","vss","ai"};for(int i=0;i<8;i++){char q[128];snprintf(q,sizeof(q),"LOAD %s",exts[i]);char tag[128];snprintf(tag,sizeof(tag),"extension_%s",exts[i]);run(con,tag,q,0);}
 run(con,"installed_extensions","SELECT extension_name,loaded,installed FROM duckdb_extensions() WHERE installed OR loaded ORDER BY extension_name",35);
 if(native_dot)register_udf(con,"sovereign_native_dot4",8,DUCKDB_TYPE_FLOAT,udf_dot4);
 if(setup_onnx(root))for(int i=0;i<model_count;i++)register_onnx_udf(con,&model_actors[i]);
 if(omni_models)register_udf(con,"sovereign_native_models",0,DUCKDB_TYPE_BIGINT,udf_models);
 if(omni_lanes)register_udf(con,"sovereign_native_lanes",0,DUCKDB_TYPE_BIGINT,udf_lanes);
 const char *names[]={"audio_manifest","metadata_vectors","audio_vibe","core_memory","onnx_actor_map","onnx_brain_integration"};
 const char *files[]={"audio_manifest_vectors.json","duckdb_metadata_vectors.parquet.bin","audio_vibe_gpu.parquet.bin","t_core_memory.parquet.bin","onnx_pydantic_langgraph_master_map.json","underutilized_onnx_brain_integration.json"};
 for(int i=0;i<6;i++){char file[PATH_MAX];snprintf(file,sizeof(file),"%s/%s",root,files[i]);temp_view(con,names[i],file,(i==0||i>=4)?"json":"parquet");}
 run(con,"mounted_source_counts","SELECT json_object('manifest',(SELECT count(*) FROM audio_manifest),'metadata',(SELECT count(*) FROM metadata_vectors),'vibe',(SELECT count(*) FROM audio_vibe),'memory',(SELECT count(*) FROM core_memory),'onnx_maps',(SELECT count(*) FROM onnx_actor_map),'brain_docs',(SELECT count(*) FROM onnx_brain_integration))::VARCHAR",1);
 run(con,"sql_native_kernel","SELECT sovereign_native_dot4(1.0::FLOAT,2.0::FLOAT,3.0::FLOAT,4.0::FLOAT,5.0::FLOAT,6.0::FLOAT,7.0::FLOAT,8.0::FLOAT) AS actual_native_dot",1);
 run(con,"sql_native_omni","SELECT json_object('models',sovereign_native_models(),'lanes',sovereign_native_lanes())::VARCHAR",1);
 run(con,"sql_native_onnx","SELECT sovereign_onnx_projection_first() AS projection,sovereign_onnx_steerer_first() AS steerer,sovereign_onnx_decoder_first() AS decoder,sovereign_onnx_rotator_first() AS rotator",1);
 run(con,"json_actor_dispatch","WITH ingress AS (SELECT json_transform('{\"actor\":\"sovereign_native_dot4\",\"runtime\":\"linux_elf\"}','{\"actor\":\"VARCHAR\",\"runtime\":\"VARCHAR\"}') AS payload) SELECT json_object('actor',payload.actor,'result',CASE WHEN payload.actor='sovereign_native_dot4' THEN sovereign_native_dot4(1.0::FLOAT,2.0::FLOAT,3.0::FLOAT,4.0::FLOAT,5.0::FLOAT,6.0::FLOAT,7.0::FLOAT,8.0::FLOAT) ELSE NULL END)::VARCHAR FROM ingress",1);
 run(con,"registered_udfs","SELECT function_name FROM duckdb_functions() WHERE function_name LIKE 'sovereign_native_%' OR function_name LIKE 'sovereign_onnx_%' ORDER BY 1",15);
 run(con,"registered_json_model_lookup","SELECT item.model_name, item.old_langgraph_node FROM onnx_actor_map,UNNEST(mappings) AS v(item) LIMIT 3",1);
 if(getenv("ROOM9_STDIN_SQL")){char line[16384];while(fgets(line,sizeof(line),stdin)){if(!strncmp(line,"QUIT",4))break;run(con,"interactive_sql",line,25);fflush(stdout);}}
 duckdb_disconnect(&con);duckdb_close(&database);if(onnx_mem)onnx_api->ReleaseMemoryInfo(onnx_mem);for(int i=0;i<model_count;i++)if(model_actors[i].session)onnx_api->ReleaseSession(model_actors[i].session);if(onnx_options)onnx_api->ReleaseSessionOptions(onnx_options);if(onnx_env)onnx_api->ReleaseEnv(onnx_env);return 0;
}
