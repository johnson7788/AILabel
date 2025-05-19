import axios from './axiosUtils.ts'

// 第1个接口, 用于测试服务端是否正常运行
namespace Ping {
  // 执行成功后返回的数据
  export interface ResData {
    response: string;
  }
}
export const pingHost = () => {
    return axios.post<Ping.ResData>('/ping', {});
}
// 第2个接口, 获取工具列表
namespace GetTools {
  // 执行成功后返回的数据
  export interface ResData {
    info: string;
  }
}
export const getTools = () => {
    // 返回的数据格式可以和服务端约定
    return axios.post<GetTools.ResData>('/api/get_tools');
}
//第3个接口, 执行工具
namespace ExecuteTool {
  // 执行工具时需要的参数
  export interface ReqForm {
    name: string;
    arguments: string;
  }
  // 执行成功后返回的数据
  export interface ResData {
    response: any;
  }
}
export const executeTool = (params: ExecuteTool.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<ExecuteTool.ResData>('/api/execute', params);
}
// 获取所有prompts
namespace GetPrompts {
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string[];
    }
  }
}
export const getPrompts = () => {
    // 返回的数据格式可以和服务端约定
    return axios.post<GetPrompts.ResData>('/api/get_prompts');
}

// 获取所有prompts对应的所有问题
namespace GetPromptsQuestions {
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string[];
    }
  }
}
export const getPromptsQuestions = () => {
    // 返回的数据格式可以和服务端约定
    return axios.post<GetPromptsQuestions.ResData>('/api/get_prompts_questions');
}

// 辅助标注的接口
namespace StartLabelChat {
  export interface ReqForm {
    prompt: string;
    messages: string[];
    llm?:string[];
    tools?:string[];
    usecache?: boolean;
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const startLabelChat = (params: StartLabelChat.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<StartLabelChat.ResData>('/api/label_chat',params);
}

// 正式测试的接口
namespace StartChat {
  export interface ReqForm {
    prompt: string;
    messages: string[];
    llm?:string;
    tools?:string[];
    additional?:{};
    usecache?: boolean;
    verbose?: boolean;
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const startChat = (params: StartChat.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<StartChat.ResData>('/api/chat',params);
}

// 查询问题的标注状态
namespace QueryLabel {
  export interface ReqForm {
    questions: string[];
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const queryQuestionLabel = (params: QueryLabel.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<QueryLabel.ResData>('/api/query_questions_label',params);
}

// 追加1条问题到问题库
namespace AppendQuestion {
  export interface ReqForm {
    question: string;
    prompt: string;
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const appendQuestion = (params: AppendQuestion.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<AppendQuestion.ResData>('/api/append_question',params);
}

// 保存一条message
namespace SaveChat {
  export interface ReqForm {
    messages: string[];
    prompt: string;
    tools?: string[];
    collection?: string;
    id?:string;
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const saveChat = (params: SaveChat.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<SaveChat.ResData>('/api/save_message',params);
}

// 删除一条message
namespace DeleteMessage {
  export interface ReqForm {
    id: string;
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const deleteMessage = (params: DeleteMessage.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<DeleteMessage.ResData>('/api/delete_message',params);
}

// 更新一条message
namespace UpdateMessage {
  export interface ReqForm {
    id: string;
    messages: string;
    prompt: string;
    tools: [string];
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const updateMessage = (params: UpdateMessage.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<UpdateMessage.ResData>('/api/update_message',params);
}


// 保存当前会话
namespace GetAllData {
  export interface ReqForm {
    mode?: string;
    limit?: number;  //限制返回数据的条数
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const getAllData = (params: GetAllData.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<GetAllData.ResData>('/api/get_all',params);
}

// 保存当前会话
namespace QueryMessageData {
  export interface ReqForm {
    keyword: string;
    field?: string;
    mode?: string;
    limit?: number;  //限制返回数据的条数
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const queryMessageData = (params: QueryMessageData.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<QueryMessageData.ResData>('/api/query_message',params);
}



// 获取总的数据量
namespace GetAllNumber {
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const getAllNumber = () => {
    // 返回的数据格式可以和服务端约定
    return axios.post<GetAllNumber.ResData>('/api/get_all_number');
}

// 清理数据库
namespace ClearAllData {
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const clearAllData = () => {
    // 返回的数据格式可以和服务端约定
    return axios.post<ClearAllData.ResData>('/api/clear');
}

// 导出数据
namespace ExportAllData {
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const exportAllData = () => {
    // 返回的数据格式可以和服务端约定
    return axios.post<ExportAllData.ResData>('/api/export');
}

// 获取所有的可用的llm
namespace GetLLM {
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string[];
    }
  }
}
export const getLLM = () => {
    // 返回的数据格式可以和服务端约定
    return axios.post<GetLLM.ResData>('/api/get_llm');
}

// 保存当前会话
namespace DeletePrompt {
  export interface ReqForm {
    name: string;
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const deletePrompt = (params: DeletePrompt.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<DeletePrompt.ResData>('/api/delete_prompt',params);
}

// 保存当前会话
namespace ModifyPrompt {
  export interface ReqForm {
    name: string;
    prompt: string;
    usage: string;
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const modifyPrompt = (params: ModifyPrompt.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<ModifyPrompt.ResData>('/api/modify_prompt',params);
}

// 增加1个prompt
namespace AddPrompt {
  export interface ReqForm {
    name: string;
    prompt: string;
    usage: string;
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const addPrompt = (params: AddPrompt.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<AddPrompt.ResData>('/api/add_prompt',params);
}

// 获取所有prompts
namespace GenerateQuestion {
  export interface ReqForm {
    prompt: string;
    tool_name?: string;
    llm?:string;
    usecache?:string;
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const generateQuestion = (params: GenerateQuestion.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<GenerateQuestion.ResData>('/api/generate_question',params);
}

// 获取所有prompts
namespace SaveQuestion {
  export interface ReqForm {
    prompt: string;
    question_content: string;
    llm:string[];
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const saveQuestion = (params: SaveQuestion.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<SaveQuestion.ResData>('/api/save_question',params);
}

// 获取所有prompts
namespace GetAllQuestion {
  export interface ReqForm {
    keyword?: string;
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const getAllQuestion = (params: GetAllQuestion.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<GetAllQuestion.ResData>('/api/get_all_questions',params);
}

// 获取所有prompts
namespace DeleteQuestion {
  export interface ReqForm {
    prompt: string;
    llm:string[];
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const deleteQuestion = (params: DeleteQuestion.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<DeleteQuestion.ResData>('/api/delete_question',params);
}

// 导出数据
namespace BackupMongo {
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const backupMongo = () => {
    // 返回的数据格式可以和服务端约定
    return axios.post<BackupMongo.ResData>('/api/backup');
}

// 获取所有prompts
namespace QueryNeo4j {
  export interface ReqForm {
    property_name: string;
    property_value: string;
    limit?: number;
  }
  // 执行成功后返回的数据
  export interface ResData {
    data: {
      code: string;
      msg: string;
      data: string;
    }
  }
}
export const queryNeo4j = (params: QueryNeo4j.ReqForm) => {
    // 返回的数据格式可以和服务端约定
    return axios.post<QueryNeo4j.ResData>('/neo4j/query',params);
}