from flask import Flask, render_template, request
import os
import yaml
import vertexai
import markdown
from vertexai.preview.generative_models import GenerativeModel, Part

app = Flask(__name__)

def get_config_value(config, section, key, default=None):
    """
    Retrieve a configuration value from a section with an optional default value.
    """
    try:
        return config[section][key]
    except:
        return default
        
with open('config.yaml') as f:
    config = yaml.safe_load(f)

TITLE = get_config_value(config, 'app', 'title', 'GeminiCraft')
SUBTITLE = get_config_value(config, 'app', 'subtitle', 'Your friendly Bot to generate social media blogs ')
CONTEXT = get_config_value(config, 'palm', 'context', 'You write social media articles about latest trends on latest technology')
BOTNAME = get_config_value(config, 'palm', 'botname', 'BlogSmith')
TEMPERATURE = get_config_value(config, 'palm', 'temperature', 0.8)
MAX_OUTPUT_TOKENS = get_config_value(config, 'palm', 'max_output_tokens', 256)
TOP_P = get_config_value(config, 'palm', 'top_p', 0.8)
TOP_K = get_config_value(config, 'palm', 'top_k', 40)



@app.route("/", methods = ['POST', 'GET'])
def main():
    if request.method == 'POST':
        input = request.form['input']
        temperature = float(request.form['temperature'])
        response, alternate = get_response(input,temperature, False)
    else: 
        input = ""
        temperature = 0.0
        response,alternate = get_response("Who are you and what can you do?",temperature, True)
        alternate = ""

    model = {"title": TITLE, "subtitle": SUBTITLE, "botname": BOTNAME, "message": markdown.markdown(response), "input": input,"temperature": temperature, "alternate": markdown.markdown(alternate)}
    return render_template('index.html', model=model)


def get_response(input,temperature, isInitial):
    vertexai.init(location="us-central1")
    parameters = {
        "temperature": temperature,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "top_p": TOP_P,
        "top_k": TOP_K
    }
    
    if not isInitial:
            context = """
            
            Instructions: You are technology bot and you will answers questions only to the technology topics.
            Context: You write social media articles about latest trends on latest technology
                            When you write an article you will be given a topic and should do the following:
                            Start with a compelling introduction that grabs attention and introduces the core theme.
                            Place hastags strategically and hastags need to be relevant and trending
                            Conclude with a strong call to action and encouraging readers to continue learning on the topic
                            Write a blogs post about {}""".format(input)
    else:
        context = input

    model = GenerativeModel("gemini-pro")
    response = model.generate_content(context, generation_config=parameters)

    parameters = {
        "temperature": temperature,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "top_p": 0.4,
        "top_k": 20
    }
    
    alternate  = model.generate_content(context,generation_config=parameters)
    return {response.text, alternate.text}
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    
