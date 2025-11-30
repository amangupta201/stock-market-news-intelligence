"""
Check available Gemini models
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai

    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ No GEMINI_API_KEY found in .env file")
        print("\nTo get a free API key:")
        print("1. Go to: https://aistudio.google.com/app/apikey")
        print("2. Click 'Create API Key'")
        print("3. Add it to your .env file as: GEMINI_API_KEY=your_key_here")
    else:
        print("🔑 API Key found!")
        print(f"   Key: {api_key[:10]}...{api_key[-4:]}")

        # Configure Gemini
        genai.configure(api_key=api_key)

        print("\n" + "=" * 60)
        print("📋 AVAILABLE GEMINI MODELS")
        print("=" * 60)

        # List all available models
        models = genai.list_models()

        generate_content_models = []

        for model in models:
            print(f"\n✅ {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description}")
            print(f"   Supported methods: {model.supported_generation_methods}")

            # Check if it supports generateContent
            if 'generateContent' in model.supported_generation_methods:
                generate_content_models.append(model.name)

        print("\n" + "=" * 60)
        print("🎯 MODELS THAT SUPPORT generateContent")
        print("=" * 60)

        if generate_content_models:
            for model_name in generate_content_models:
                print(f"  ✅ {model_name}")

            print("\n" + "=" * 60)
            print("💡 RECOMMENDED MODEL TO USE")
            print("=" * 60)

            # Find the best model
            if any('gemini-1.5-flash' in m for m in generate_content_models):
                recommended = [m for m in generate_content_models if 'gemini-1.5-flash' in m][0]
            elif any('gemini-pro' in m for m in generate_content_models):
                recommended = [m for m in generate_content_models if 'gemini-pro' in m][0]
            else:
                recommended = generate_content_models[0]

            print(f"\n  Use this in your code: '{recommended}'")
            print(f"\n  Example:")
            print(f"    model = genai.GenerativeModel('{recommended}')")
        else:
            print("\n  ⚠️  No models support generateContent")
            print("     Your API key might not have access to generation models")

except ImportError:
    print("❌ google-generativeai not installed")
    print("\nInstall it with:")
    print("  pip install google-generativeai")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\nMake sure:")
    print("1. google-generativeai is installed: pip install google-generativeai")
    print("2. GEMINI_API_KEY is set in your .env file")
    print("3. Your API key is valid (get it from https://aistudio.google.com/app/apikey)")