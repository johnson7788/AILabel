import {
    createRouter,
    createWebHistory,
} from "vue-router";

const routes = [
    {
        path: '/',
        name: "homeindex",
        component: () => import("../home/Home.vue"),
    },
    {
        path: '/labelchat',
        name: "labelchat",
        redirect: "/labelchat/login",
        children: [
            {
                path: "/labelchat/home",
                name: "labelhome",
                component: () => import("../projects/labelchat/index.vue"),
            },
            {
                path: "/labelchat/label",
                name: "labelpage",
                component: () => import("../projects/labelchat/label.vue"),
            },
            {
                path: "/labelchat/labelAgent",
                name: "labelAgentpage",
                component: () => import("../projects/labelchat/labelAgent.vue"),
            },
            {
                path: "/labelchat/labelBeautyAgent",
                name: "labelBeAgentpage",
                component: () => import("../projects/labelchat/labelBeautyAgent.vue"),
            },
            {
                path: "/labelchat/prelabel",
                name: "prelabel",
                component: () => import("../projects/labelchat/prelabel.vue"),
            },
            {
                path: "/labelchat/prelabelAgent",
                name: "prelabelAgent",
                component: () => import("../projects/labelchat/prelabelAgent.vue"),
            },
            {
                path: "/labelchat/prelabelBeautyAgent",
                name: "prelabelBeautyAgent",
                component: () => import("../projects/labelchat/prelabelBeautyAgent.vue"),
            },
            {
                path: "/labelchat/review",
                name: "labelreview",
                component: () => import("../projects/labelchat/review.vue"),
            },
            {
                path: "/labelchat/stats",
                name: "labelstatistics",
                component: () => import("../projects/labelchat/statistics.vue"),
            },
            {
                path: "/labelchat/sample",
                name: "labelsample",
                component: () => import("../projects/labelchat/sample.vue"),
            },
            {
                path: "/labelchat/instruction_generation",
                name: "labelinstructionGeneration",
                component: () => import("../projects/labelchat/instructionGeneration.vue"),
            },
            {
                path: "/labelchat/instruction_generation_agent",
                name: "labelinstructionGenerationAgent",
                component: () => import("../projects/labelchat/instructionGenerationAgent.vue"),
            },
            {
                path: "/labelchat/instruction_generation_Beautyagent",
                name: "instructionGenerationBeautyAgent",
                component: () => import("../projects/labelchat/instructionGenerationBeautyAgent.vue"),
            },
            {
                path: "/labelchat/instruction_filter",
                name: "labelinstructionFilter",
                component: () => import("../projects/labelchat/instructionFilter.vue"),
            },
            {
                path: "/labelchat/tools_manage",
                name: "labeltoolsManage",
                component: () => import("../projects/labelchat/toolsManage.vue"),
            },
            {
                path: "/labelchat/tools_generation",
                name: "labeltoolsGeneration",
                component: () => import("../projects/labelchat/toolsGeneration.vue"),
            },
            {
                path: "/labelchat/prompt",
                name: "labelprompt",
                component: () => import("../projects/labelchat/prompt.vue"),
            },
            {
                path: "/labelchat/manage",
                name: "labelmanage",
                component: () => import("../projects/labelchat/manage.vue"),
            },
            {
                path: "/labelchat/test",
                name: "labeltest",
                component: () => import("../projects/labelchat/ceshitest.vue"),
            },
            {
                path: "/labelchat/verify",
                name: "labelverify",
                component: () => import("../projects/labelchat/verify.vue"),
            },
            {
                path: "/labelchat/document",
                name: "labeldocument",
                component: () => import("../projects/labelchat/document.vue"),
            },
            {
                path: "/labelchat/login",
                name: "labellogin",
                component: () => import("../projects/labelchat/login.vue"),
            },
        ]
    } 
]

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;