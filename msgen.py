import streamlit as st
import anthropic
import datetime
import os
import xml.etree.ElementTree as ET
import re
import random
import time

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


def donation_appeal():
    donation_url = 'https://ko-fi.com/mightylittledev'
    st.markdown(f'<a href="{donation_url}" target="_blank">Support the development, maintenance and operational costs of this tool with a donation</a>', unsafe_allow_html=True)


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
    bypass_llm = st.checkbox("Bypass LLM", value=True)

donation_appeal()

# Create submit button
if st.button("Enhance Message"):
    # Create a placeholder for the "Analyzing..." label and stopwatch
    analysis_placeholder = st.empty()
    
    start_time = time.time()
    
    if bypass_llm:
        # Simulate API call delay
        for i in range(3):  # Simulate 3 seconds of processing
            elapsed_time = time.time() - start_time
            analysis_placeholder.write(f"Analyzing... Time elapsed: {elapsed_time:.2f} seconds")
            time.sleep(1)
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
            with st.spinner("Analyzing..."):
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
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

    # Clear the analysis placeholder
    analysis_placeholder.empty()

    # Calculate and display the total time taken
    end_time = time.time()
    total_time = end_time - start_time
    st.success(f"Enhancement and analysis completed in {total_time:.2f} seconds")

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
    
    st.markdown("### No words changed, only emojis added")
    st.text_area("Original text with emojis added", root.find('no_word_change').text, height=400, label_visibility="hidden")
            
    st.markdown("### Text enhanced, emojis also added")
    st.text_area("Enhanced text with emojis added", root.find('word_change').text, height=400, label_visibility="hidden")

    st.markdown("## Improvement Suggestions")
    
    st.markdown("### Spelling and Grammar Mistakes")
    st.markdown(root.find('spelling_grammar_mistakes').text)
    
    st.markdown("### Logical Inconsistencies")
    st.markdown(root.find('logical_inconsistencies').text)
    
    st.markdown("### Temporal Inconsistencies")
    st.markdown(root.find('temporal_inconsistencies').text)
    
    st.markdown("### Missing Information / Needs more clarity")
    st.markdown(root.find('missing_information').text)

    donation_appeal()