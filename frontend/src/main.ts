import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { config as mdEditorConfig } from 'md-editor-v3'
import './style.css'
import App from './App.vue'
import router from './router'

// 关闭 md-editor-v3 自带的 linkShortener：默认正则会把任意以 "/" 开头、超过 30
// 字符的子串（包括中文里嵌入的 "商业/产品行业..."）替换成可点击展开的 "..." widget，
// 表现就像内容被自动折叠。整段禁用以恢复"所见即所得"。
mdEditorConfig({
  codeMirrorExtensions(extensions) {
    return extensions.filter(e => e.type !== 'linkShortener')
  },
})

createApp(App).use(createPinia()).use(router).mount('#app')
