import { defineComponent } from 'vue'

const HelloWorld = defineComponent({
    props: {
        msg: {
            type: String,
            default: 'Hello World'
        }
    },
    setup(props) {
        return () => (
            <div>
                <h1>{props.msg}</h1>
                <h1>{props.msg}</h1>
                <h1>{props.msg}</h1>
            </div>
        )
    }
})

export default HelloWorld
