import streamlit as st
import anthropic
import datetime
import os
import xml.etree.ElementTree as ET
import re
import random


# Function to check if we're in debug mode
def is_ui_debug_mode():
    return 'uidebug' in st.query_params


def generate_random_data():
    """Generate random data for testing purposes."""
    emojis = ["😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇"]
    
    random_text = lambda: " ".join([random.choice(["Lorem", "ipsum", "dolor", "sit", "amet"]) for _ in range(20)])
    random_emojis = lambda: "".join([random.choice(emojis) for _ in range(random.randint(1, 5))])
    
    return f"""
    <output>
        <no_word_change>{random_text()} {random_emojis()}</no_word_change>
        <word_change>{random_text()} {random_emojis()}</word_change>
        <spelling_grammar_mistakes>{random.choice(["No mistakes found.", "Found a few typos.", "Grammar could be improved."])}</spelling_grammar_mistakes>
        <logical_inconsistencies>{random.choice(["No inconsistencies found.", "Check the date mentioned.", "Verify the event location."])}</logical_inconsistencies>
        <temporal_inconsistencies>{random.choice(["Dates seem correct.", "Ensure the timeline is consistent.", "Check if all events are in chronological order."])}</temporal_inconsistencies>
        <missing_information>{random.choice(["All necessary information seems to be present.", "Consider adding contact details.", "The event duration is not specified."])}</missing_information>
    </output>
    """


# Add a title to the webapp
st.title("Message Enhancement and Analysis Tool")

# Create input elements
og_message = st.text_area("Enter your message here:", height=400)
col1, col2 = st.columns(2)
with col1:
    output_emoji_level = st.slider("Output Emoji Level", 0, 5, 5)
with col2:
    message_type = st.selectbox("Message Type", ["Event", "General"])

# Only show the bypass checkbox if in debug mode
bypass_llm = False
if is_ui_debug_mode():
    bypass_llm = st.checkbox("Bypass LLM", value=False)

# Create submit button
if st.button("Enhance Message"):
    if bypass_llm:
        content = generate_random_data()
    else:
        # Form XML input
        today = datetime.date.today().isoformat()
        input_xml = f"""
        <input>
        <og_message>{og_message}</og_message>
        <message_type>{message_type}</message_type>
        <today>{today}</today>
        <check_proper_nouns>CHYK, Chyk, Chinmaya, Chinmayananda, Yuva, Kendra, Mission, Swami, Swamiji, Chidrupananda, Noida, CCMT, Devi, Shiva, Hanuman, Krishna, Rama</check_proper_nouns>
        <output_emoji_level>{output_emoji_level}</output_emoji_level>
        </input>
        """

        # Read system message from file
        with open("system_message.txt", "r") as file:
            system_message = file.read()

        # Make API call to Anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            st.error("Required environment variables not set.")
            st.stop()
        
        client = anthropic.Anthropic(api_key=api_key)
        try:
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=3000,
                temperature=0,
                system=system_message,
                messages=[{"role": "user", "content": input_xml}]
            )

            # Extract the content from the response
            content = response.content[0].text

            # Remove any non-XML content before the opening <output> tag
            content = re.sub(r'^.*?(?=<output>)', '', content, flags=re.DOTALL)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.stop()

    # Parse the XML response
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        st.error(f"Failed to parse XML response: {str(e)}")
        st.text("Raw response:")
        st.text(content)
        st.stop()

    # Display results
    st.markdown("## Enhancements")
    
    st.markdown("### Original Text with emojis added")
    st.text_area("Original text with emojis added", root.find('no_word_change').text, height=400, label_visibility="hidden")  # Increased height
            
    st.markdown("### Enhanced Text with emojis added")
    st.text_area("Enhanced text with emojis added", root.find('word_change').text, height=400, label_visibility="hidden")  # Increased height

    st.markdown("## Improvement Suggestions")
    
    st.markdown("### Spelling and Grammar Mistakes")
    st.markdown(root.find('spelling_grammar_mistakes').text)
    
    st.markdown("### Logical Inconsistencies")
    st.markdown(root.find('logical_inconsistencies').text)
    
    st.markdown("### Temporal Inconsistencies")
    st.markdown(root.find('temporal_inconsistencies').text)
    
    st.markdown("### Missing Information / Needs more clarity")
    st.markdown(root.find('missing_information').text)
