import streamlit as st
import anthropic
import datetime
import os
import xml.etree.ElementTree as ET
import re

# Add a title to the webapp
st.title("Message Enhancement and Analysis Tool")

# Create input elements
og_message = st.text_area("Enter your message here:", height=350)  # Increased height
col1, col2 = st.columns(2)
with col1:
    output_emoji_level = st.slider("Output Emoji Level", 0, 5, 5)
with col2:
    message_type = st.selectbox("Message Type", ["Event", "General"])

# Create submit button
if st.button("Enhance Message"):
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
        st.error("Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable.")
    else:
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

            # Parse the XML response
            try:
                root = ET.fromstring(content)
            except ET.ParseError as e:
                st.error(f"Failed to parse XML response: {str(e)}")
                st.text("Raw response:")
                st.text(content)
                st.stop()

            # Display results
            st.subheader("Analysis Results")
            
            st.text_area("Original Text with emojis added", root.find('no_word_change').text, height=350)  # Increased height
            st.text_area("Enhanced Text with emojis added", root.find('word_change').text, height=350)  # Increased height

            st.subheader("Improvement Suggestions")
            st.write("Spelling and Grammar Mistakes:")
            st.write(root.find('spelling_grammar_mistakes').text)
            
            st.write("Logical Inconsistencies:")
            st.write(root.find('logical_inconsistencies').text)
            
            st.write("Temporal Inconsistencies:")
            st.write(root.find('temporal_inconsistencies').text)
            
            st.write("Potentially Missing Information:")
            st.write(root.find('missing_information').text)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            if 'response' in locals():
                st.text("Raw response:")
                st.text(response.content)