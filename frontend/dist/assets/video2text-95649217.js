import{d as z,g as a,h as j,o as c,b as i,f as A,A as p,B as F,a as e,F as D,e as L,t as d,z as y,P as B,j as G,E as b}from"./index-f50d6d08.js";import{a as I}from"./axios-a342f982.js";import{l as W}from"./index-e3f35709.js";import{G as q,C as J,_ as O,h as R}from"./navbar.vue_vue_type_script_setup_true_lang-1f4df18c.js";const X={class:"main"},H=e("h1",null," 视频或音频转换成文本，上传，转换，下载 ",-1),K={class:"my-auto"},P=["value"],Q={key:0},Y={class:"mt-6"},Z=e("span",null,"选择1个视频或音频文件：",-1),ee=["value"],se=e("option",{value:"zh"},"Chinese",-1),te=e("option",{value:"en"},"English",-1),oe=[se,te],le={class:"loading loading-spinner"},ae={key:0,class:"mt-4 whitespace-pre-line"},ne=e("h3",{class:"text-lg font-bold"},"消息:",-1),ue={key:1,class:"mt-4 whitespace-pre-line"},ce=e("h3",{class:"text-lg font-bold"},"结果:",-1),ie={key:2,class:"mt-4 text-red-500 whitespace-pre-line"},re=e("h3",{class:"text-lg font-bold"},"错误:",-1),ge=z({__name:"video2text",setup(de){const S="https://ai.minitool.fun:15554",V=a([]),w=a(),m=a([]),u=a([]),r=a(""),$=a(!1),_=a(!1),x=a("zh"),C=a(""),g=a(null),h=a(null),n=a(null),E=localStorage.getItem("access_token")||"",N=()=>{n.value||(n.value=W(S,{query:{token:E},path:"/socket_for_audio"}),n.value.on("connect",()=>{console.log("Connected to server")}),n.value.on("message",t=>{console.log(t),t.content&&(C.value+=t.content+`
`),console.log(t.content)}),n.value.on("result",t=>{g.value=t.content,_.value=!1}),n.value.on("error",t=>{h.value=t.content}),n.value.on("disconnect",()=>{console.log("Disconnected from server")}))},M=()=>{_.value=!0,n.value||N(),g.value=null,h.value=null,n.value.connected?n.value.emit("start_video2text",{video_file:w.value,language:x.value}):console.error("WebSocket connection not established")},T=(t,o)=>{const s=t.target;s.files&&(m.value=Array.from(s.files),u.value=m.value.map(l=>({name:l.name,progress:0})),m.value.forEach((l,v)=>{o==="image"&&!l.type.startsWith("image/")?(r.value=`文件 ${l.name} 不是图片格式，上传失败`,u.value[v].progress=-1):o==="mind"&&!["application/json","application/vnd.xmind.workbook"].includes(l.type)?(r.value=`文件 ${l.name} 不是 JSON 或 XMind 格式，上传失败`,u.value[v].progress=-1):U(l,v)}),m.value=null)},U=(t,o)=>{if(!t){b({title:"success",message:"需要选择1个文件"});return}const s=new FormData;s.append("file",t);const l={...R};delete l["Content-Type"];let v=`${S}/mind/upload_file`;I.post(v,s,{headers:{"Content-Type":"multipart/form-data",...l},onUploadProgress:f=>{u.value[o]&&(u.value[o].progress=Math.round(f.loaded*100/f.total))}}).then(f=>{const k=f.data;k.code===0?(r.value="文件上传成功",b({title:"success",message:`文件上传: ${k.msg}`}),u.value[o].progress=100):(r.value=`文件上传失败: ${k.msg}`,b({title:"success",message:`文件上传: ${k.msg}`}),u.value[o].progress=-1)}).catch(()=>{r.value="文件上传失败",u.value[o].progress=-1,b({title:"error",message:"文件上传失败，服务器异常"})})};return j(async()=>{const t=await q();V.value=t.files,$.value=await J(),N()}),(t,o)=>(c(),i("div",X,[A(O),H,p(e("div",K,[e("input",{type:"file",class:"file-input file-input-bordered file-input-success w-full max-w-xs h-16",onChange:o[0]||(o[0]=s=>T(s,"mind"))},null,32),(c(!0),i(D,null,L(u.value,(s,l)=>(c(),i("div",{key:l},[e("p",null,d(s.name)+" 上传进度: "+d(s.progress)+"%",1),e("progress",{value:s.progress,max:"100"},null,8,P)]))),128)),r.value?(c(),i("div",Q,d(r.value),1)):y("",!0)],512),[[F,$.value]]),e("div",Y,[Z,p(e("select",{class:"select select-accent w-full max-w-xs","onUpdate:modelValue":o[1]||(o[1]=s=>w.value=s)},[(c(!0),i(D,null,L(V.value,s=>(c(),i("option",{value:s.name},d(s.name),9,ee))),256))],512),[[B,w.value]]),e("div",null,[p(e("select",{"onUpdate:modelValue":o[2]||(o[2]=s=>x.value=s),class:"mb-4 p-2 border rounded"},oe,512),[[B,x.value]])]),e("div",null,[e("button",{class:"btn btn-success ml-6",onClick:M},[p(e("span",le,null,512),[[F,_.value]]),p(e("span",null,"loading",512),[[F,_.value]]),G(" 转换 ")])])]),C.value?(c(),i("div",ae,[ne,e("p",null,d(C.value),1)])):y("",!0),g.value?(c(),i("div",ue,[ce,e("p",null,d(g.value),1)])):y("",!0),h.value?(c(),i("div",ie,[re,e("p",null,d(h.value),1)])):y("",!0)]))}});export{ge as default};
