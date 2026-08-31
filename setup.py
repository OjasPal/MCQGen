from setuptools import setup, find_packages

setup(
    name='mcqgenerator',
    version= '0.0.1',
    author='Ojas Pal',
    author_email='moneyunlimited010@gmail.com',
    install_requires=["langchain", "langchain-community", "langchain-groq", "streamlit", "python-dotenv", "PyPDF2"],
    packages=find_packages()
)