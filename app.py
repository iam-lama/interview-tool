from openai import OpenAI
import streamlit as st
#from streamlit_js_eval import streamlit_js_eval

from streamlit.components.v1 import html


st.set_page_config(page_title='Streamlit Chat', page_icon='')
st.title('chatbot')

if "setup_complete" not in st.session_state:
    st.session_state['setup_complete'] = False
if "user_messages_count" not in st.session_state:
    st.session_state['user_messages_count'] = 0
if "feedback_shown" not in st.session_state:
    st.session_state['feedback_shown'] = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_complete" not in st.session_state:
    st.session_state['chat_complete'] = False



def complete_setup():
    st.session_state.setup_complete = True
def show_feedback():
    st.session_state.feedback_shown = True


if not st.session_state.setup_complete:
    st.subheader('Personal Information', divider='rainbow')

    if 'name' not in st.session_state:
        st.session_state['name'] = ''
    if 'experience' not in st.session_state:
        st.session_state['experience'] = ''
    if 'skills' not in st.session_state:
        st.session_state['skills'] = ''

    st.session_state['name'] = st.text_input(label='Name', max_chars=40, value= st.session_state['name'], placeholder='Enter your name')
    st.session_state['experience'] = st.text_area(label='Experience', value = st.session_state['experience'] , height=None, max_chars=200, placeholder='Descripe your experience')
    st.session_state['skills'] = st.text_area(label='Skills', value= st.session_state['skills'] , height=None, max_chars=200, placeholder='List your skills')

   ## st.write(f"**Your name**: {st.session_state['name']}")
   ## st.write(f"**Your experience**:  {st.session_state['experience']}")
   ## st.write(f"**Your skills**: {st.session_state['skills']}")

    if 'level' not in st.session_state:
        st.session_state['level'] = 'Junior'
    if 'position' not in st.session_state:
        st.session_state['position'] = 'Data Scientest'
    if 'company' not in st.session_state:
        st.session_state['company'] = 'Meta'
   
    col1, col2 = st.columns(2)
    with col1:
        st.session_state['level'] = st.radio(label="Choose Level", 
                        key="visibility",
                        options=['Junior','Med-level','Senior'],
                        )

    with col2:
        st.session_state['position'] = st.selectbox(
            'Choose Position',
            ('Data Scientest', 'Data Engineer', 'ML Engineer', 'BI Analyist', 'Financial Analyist'),
        )

    st.session_state['company'] = st.selectbox(
            'Choose Company',
            ('Meta', 'Apple', 'Udemy', '365 Company', 'Rowaq', 'Misk'),
        )

    #st.write(f"**Your Information**: {st.session_state['level']} {st.session_state['position']} at { st.session_state['company']}")

    if st.button("Start Interview", on_click=complete_setup):
        st.write("Starting interview...")



if  st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:
    st.info(
        '''
        Start by introducing yourself.
        ''',
    )
    client= OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if 'openai_model' not in st.session_state:
        st.session_state['openai_model'] = 'gpt-4o-mini'

    if  not st.session_state.messages:
        st.session_state.messages = [{"role": "system", 
                                    "content":f"You are an HR excutive that interview an interviewee called { st.session_state['name']} \
                                        with experience { st.session_state['experience']} and skills { st.session_state['skills']}. \
                                            You should interview him for position { st.session_state['level']} { st.session_state['position']} \
                                                at company { st.session_state['company']}"}]

    for messages in st.session_state.messages:
        if messages['role'] != 'system':
            with st.chat_message(messages['role']):
                st.markdown(messages['content'])


    if st.session_state.user_messages_count < 5:
        if prompt:= st.chat_input('Yor answer:', max_chars=200):
            st.session_state.messages.append({'role':'user', 'content':prompt })
            with st.chat_message('user'):
                st.markdown(prompt)

            if st.session_state.user_messages_count < 4:
                with st.chat_message('assistant'):
                    stream = client.chat.completions.create(
                        model = st.session_state['openai_model'],
                        messages = [
                            {'role':m['role'], 'content':m['content']}
                            for m in st.session_state.messages
                        ],
                        stream = True
                    )
                    response = st.write_stream(stream)
                    st.session_state.messages.append({'role':'assistant', 'content':response})
            
            st.session_state.user_messages_count+= 1
    
    if st.session_state.user_messages_count >= 5:
        st.session_state.chat_complete = True

if not st.session_state.feedback_shown and st.session_state.chat_complete:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Fetching feedback...")

if st.session_state.feedback_shown:
    st.subheader("Feedback")
    
    conversation_history = "\n".join([f"{msg['role']}:{msg['content']}" for msg in st.session_state.messages])

    feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    feedback_completion = feedback_client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {
                "role":"system",
                "content":"""You are a helpful tool that provides feedback on an interviiewee performance.
                 Before the Feedback give a score of 1 to 10.
                 Follow this format:
                 Overall Score: //your score
                 Feedback: //Your feedback here
                 Give only the feedback don't ask any additional questions."""

            },
            {"role": "user",
             "content": f"This is the interviwee that you need to evaluate. Keep in mind that you are only a tool and shouldn't engage in conversation {conversation_history}"}
        ]

    )
    st.write(feedback_completion.choices[0].message.content)

    if st.button("Resatrt Interview", type="primary"):
        #streamlit_js_eval(js_expressions = "parent.window.location.reload()" )
        html("<script>parent.window.location.reload()</script>")