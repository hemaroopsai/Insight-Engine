<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Insight Engine - Project README</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Poppins', sans-serif;
        }
        .code-block {
            background-color: #1f2937; /* A dark color for the code block */
            color: #d1d5db; /* A light color for the text */
            padding: 1.5rem;
            border-radius: 0.75rem;
            font-family: 'Courier New', Courier, monospace;
            overflow-x: auto;
            border: 1px solid #374151;
        }
        .code-block pre {
            margin: 0;
        }
    </style>
</head>
<body class="bg-gray-50 text-gray-800 antialiased">

    <div class="container mx-auto max-w-4xl px-4 py-12 md:py-20">

        <!-- Header Section -->
        <header class="text-center mb-12">
            <h1 class="text-5xl md:text-6xl font-bold text-gray-900">
                Insight Engine <span class="text-4xl">🧠</span>
            </h1>
            <p class="mt-4 text-lg text-gray-600">
                An intelligent research assistant built with Streamlit, FastAPI, and Google's Gemini API.
            </p>
        </header>

        <!-- About The Project Section -->
        <section class="mb-12">
            <h2 class="text-3xl font-bold border-b pb-3 mb-6 text-gray-900">🌟 About The Project</h2>
            <p class="text-gray-700 leading-relaxed">
                Insight Engine is a powerful RAG (Retrieval-Augmented Generation) application that transforms any web article or local document into a knowledgeable source you can chat with. Instead of manually searching through long texts, you can simply ask questions in natural language and get instant, accurate answers.
            </p>
            <p class="mt-4 text-gray-700 leading-relaxed">
                This project is built with a modern, decoupled architecture, featuring a powerful FastAPI backend for all AI processing and a beautiful, interactive Streamlit frontend for the user experience.
            </p>
        </section>

        <!-- Key Features Section -->
        <section class="mb-12">
            <h2 class="text-3xl font-bold border-b pb-3 mb-6 text-gray-900">✨ Key Features</h2>
            <ul class="space-y-4">
                <li class="flex items-start">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-indigo-500 mr-3 mt-1 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>
                    <span><strong>Process Multiple Sources:</strong> Analyze content from multiple URLs or upload your own PDF and TXT files.</span>
                </li>
                <li class="flex items-start">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-indigo-500 mr-3 mt-1 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
                    <span><strong>Conversational Chat:</strong> Engage in a natural, back-and-forth conversation. The app remembers the context of your previous questions.</span>
                </li>
                <li class="flex items-start">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-indigo-500 mr-3 mt-1 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                    <span><strong>Instant Summarization:</strong> Get a concise summary of all your processed documents with a single click.</span>
                </li>
                <li class="flex items-start">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-indigo-500 mr-3 mt-1 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l1.5-4.5M4.5 6a9 9 0 1118 0 9 9 0 01-18 0z"/></svg>
                    <span><strong>Multilingual Support:</strong> Ask questions in over 50 languages and get answers in the same language.</span>
                </li>
                 <li class="flex items-start">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-indigo-500 mr-3 mt-1 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
                    <span><strong>Beautiful UI:</strong> A clean, modern, and responsive user interface with dynamic light and dark modes.</span>
                </li>
            </ul>
        </section>

        <!-- Built With Section -->
        <section class="mb-12">
            <h2 class="text-3xl font-bold border-b pb-3 mb-6 text-gray-900">🛠️ Built With</h2>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div class="bg-white p-4 rounded-lg shadow-md text-center">FastAPI</div>
                <div class="bg-white p-4 rounded-lg shadow-md text-center">Streamlit</div>
                <div class="bg-white p-4 rounded-lg shadow-md text-center">LangChain</div>
                <div class="bg-white p-4 rounded-lg shadow-md text-center">Google Gemini API</div>
                <div class="bg-white p-4 rounded-lg shadow-md text-center">Chroma DB</div>
                <div class="bg-white p-4 rounded-lg shadow-md text-center">Hugging Face</div>
            </div>
        </section>

        <!-- Getting Started Section -->
        <section>
            <h2 class="text-3xl font-bold border-b pb-3 mb-6 text-gray-900">🚀 Getting Started</h2>
            
            <h3 class="text-2xl font-semibold mt-8 mb-4">Prerequisites</h3>
            <ul class="list-disc list-inside space-y-2">
                <li>Python 3.9+</li>
                <li>An API Key from <a href="https://aistudio.google.com/" class="text-indigo-600 hover:underline" target="_blank">Google AI Studio</a></li>
            </ul>

            <h3 class="text-2xl font-semibold mt-8 mb-4">Installation & Setup</h3>
            <div class="space-y-6">
                <div>
                    <h4 class="font-semibold text-lg">1. Clone the repository:</h4>
                    <div class="code-block mt-2">
                        <pre><code>git clone https://github.com/hemaroopsai/Insight-Engine.git
cd Insight-Engine</code></pre>
                    </div>
                </div>

                <div>
                    <h4 class="font-semibold text-lg">2. Create and activate a virtual environment:</h4>
                    <div class="code-block mt-2">
                        <pre><code># For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate</code></pre>
                    </div>
                </div>

                <div>
                    <h4 class="font-semibold text-lg">3. Install the required packages:</h4>
                    <div class="code-block mt-2">
                        <pre><code>pip install -r requirements.txt</code></pre>
                    </div>
                </div>

                 <div>
                    <h4 class="font-semibold text-lg">4. Create a `.env` file:</h4>
                    <p class="mt-1">Create a new file named `.env` in the root of your project and add your Google API key:</p>
                    <div class="code-block mt-2">
                        <pre><code>GOOGLE_API_KEY="YOUR_API_KEY_HERE"</code></pre>
                    </div>
                </div>
            </div>

            <h3 class="text-2xl font-semibold mt-8 mb-4">How to Run the Application</h3>
             <p class="mt-1">This project requires two separate terminals to run the backend API and the frontend UI.</p>
            <div class="space-y-6 mt-4">
                <div>
                    <h4 class="font-semibold text-lg">1. Start the Backend API:</h4>
                     <p class="mt-1">Open a terminal, navigate to your project, activate the venv, and run:</p>
                    <div class="code-block mt-2">
                        <pre><code>uvicorn api:app --reload</code></pre>
                    </div>
                </div>
                 <div>
                    <h4 class="font-semibold text-lg">2. Start the Frontend UI:</h4>
                     <p class="mt-1">Open a second terminal, navigate to your project, activate the venv, and run:</p>
                    <div class="code-block mt-2">
                        <pre><code>streamlit run Main.py</code></pre>
                    </div>
                </div>
            </div>
        </section>

    </div>

</body>
</html>
