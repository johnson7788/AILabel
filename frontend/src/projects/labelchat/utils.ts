import { toRefs } from 'vue';
import { ElNotification } from 'element-plus';
import { useMessageStore, useSettings } from './store.ts';
import { executeTool } from './api.ts'
const { currentQuestion, messages, function_results, need_summary, display_neo4j_meta, display_plot_meta } = toRefs(useMessageStore());

function getType(value) {
    //判断数据类型
    if (value instanceof Array) {
        return 'array';
    } else if (value instanceof Date) {
        return 'date';
    } else if (value instanceof RegExp) {
        return 'regexp';
    } else {
        return typeof value;
    }
};

export async function RunFunction() {
    //获取当前的question中的内容
    let question = ""
    if (currentQuestion.value.question) {
        question = currentQuestion.value.question
    } else {
        const last_message_role = messages.value[messages.value.length - 1].role
        if (last_message_role === "function_call") {
            question = messages.value[messages.value.length - 1].content
        } else {
            ElNotification.error("当前输入中为空而且上一条消息也不是函数调用，无法运行函数")
            return
        }
    }
    let params = JSON.parse(question)
    const params_type = getType(params)
    //如果参数是对象，则转换为数组
    if (params_type === "object") {
        params = [params]
    }
    //调用函数，得到返回值
    for (let one_params of params) {
        try {
            const result = await executeTool(one_params)
            const data = result.data
            console.log("Function result:", data)
            if (result.code === 0 && data.status) {
                if (data.msg.includes("Traceback")) {
                    ElNotification({
                        message: `运行函数失败，请检查输入参数或者api,错误信息包括Traceback：${data.msg}`,
                        type: 'error',
                    });
                    return
                }
                function_results.value.push(data);
                need_summary.value = data.need_summary;  //是否需要对工具的输出进行下一步summary
                if (data.meta.plot === "neo4j") {
                    display_neo4j_meta.value = data.meta.data; //获取结果中的meta信息，用于显示和绘图等
                } else if (data.meta.plot === "echarts") {
                    display_plot_meta.value = data.meta; //获取结果中的meta信息，用于显示和绘图等
                }
                ElNotification({
                    message: '函数运行成功, 是否需要summary:' + data.need_summary,
                    type: 'info',
                })
            } else {
                ElNotification({
                    message: `运行函数失败，请检查输入参数或者api,错误代码出现：${data.msg}`,
                    type: 'error',
                });
            }
        } catch (error) {
            ElNotification({
                message: `运行函数失败，请检查输入参数或者api,错误没有调用成功：${error}`,
                type: 'error',
            });
        }
    }
};

