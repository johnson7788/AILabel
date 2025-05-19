import { defineComponent } from 'vue'

const HelloWorld = defineComponent({
    props: {
        msg: {
            type: String,
            required: true
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
