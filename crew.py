from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

load_dotenv()


def build_crew(topic: str, task_callback=None) -> Crew:
    search_tool = SerperDevTool()

    researcher = Agent(
        role="Trend Researcher",
        goal=f"Find the most trending and hot subtopics related to '{topic}' using Google search.",
        backstory=(
            "You are an expert internet researcher. You use Google search to discover "
            "what is currently trending and what audiences care about most."
        ),
        tools=[search_tool],
        allow_delegation=False,
        verbose=True,
    )

    writer = Agent(
        role="Content Writer",
        goal=f"Write a highly engaging, well-structured article about '{topic}' based on the research.",
        backstory=(
            "You are a skilled content writer who turns research into engaging, "
            "easy-to-read articles that hook readers from the first sentence."
        ),
        allow_delegation=False,
        verbose=True,
    )

    seo_specialist = Agent(
        role="SEO Specialist",
        goal=f"Optimize the article about '{topic}' for SEO so it ranks well on search engines.",
        backstory=(
            "You are an SEO expert who improves content with the right keywords, "
            "meta description, headings, and readability while keeping the message clear."
        ),
        allow_delegation=False,
        verbose=True,
    )

    research_task = Task(
        description=(
            f"Search Google for the topic '{topic}'. "
            "Identify the hottest, most trending subtopics, questions people ask, "
            "and key points being discussed online right now. "
            "Summarize your findings into clear bullet points."
        ),
        expected_output=(
            "A bullet-point list of trending subtopics, popular questions, "
            "and key insights about the topic."
        ),
        agent=researcher,
    )

    writing_task = Task(
        description=(
            f"Using the research findings, write an engaging article about '{topic}'. "
            "It should have a catchy title, an introduction, clear sections with headings, "
            "and a strong conclusion. Make it informative and enjoyable to read."
        ),
        expected_output="A complete, engaging article in markdown format.",
        agent=writer,
        context=[research_task],
    )

    seo_task = Task(
        description=(
            "Review the article and optimize it for SEO. "
            "Add a meta description, ensure proper use of headings (H1, H2, H3), "
            "include relevant keywords naturally, improve readability, "
            "and add a short list of suggested SEO keywords at the end. "
            "Return the final SEO-optimized article in markdown."
        ),
        expected_output=(
            "The final SEO-optimized article in markdown, including a meta description "
            "at the top and a list of target keywords at the bottom."
        ),
        agent=seo_specialist,
        context=[writing_task],
    )

    return Crew(
        agents=[researcher, writer, seo_specialist],
        tasks=[research_task, writing_task, seo_task],
        process=Process.sequential,
        task_callback=task_callback,
        verbose=True,
    )


def run_crew(topic: str, task_callback=None) -> str:
    crew = build_crew(topic, task_callback=task_callback)
    result = crew.kickoff(inputs={"topic": topic})
    return str(result)
