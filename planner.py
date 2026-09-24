def decide_tool(user_input):

    text = user_input.lower().strip()

    # ========================================================
    # CALCULATOR
    # ========================================================

    if any(symbol in text for symbol in ["+", "-", "*", "/", "%"]):
        return "calculator"


    # ========================================================
    # CURRENT TIME
    # ========================================================

    if "time" in text:
        return "get_current_time"


    # ========================================================
    # PDF / RAG KEYWORDS
    # ========================================================

    pdf_keywords = [

        # ----------------------------------------------------
        # DBMS / DATABASE
        # ----------------------------------------------------

        "dbms",
        "database",
        "normalization",
        "normal form",
        "1nf",
        "2nf",
        "3nf",
        "bcnf",
        "sql",
        "transaction",
        "primary key",
        "foreign key",
        "candidate key",
        "super key",
        "acid",
        "index",
        "relational",
        "relation",
        "functional dependency",
        "er model",
        "entity relationship",
        "database management",


        # ----------------------------------------------------
        # ARTIFICIAL INTELLIGENCE
        # ----------------------------------------------------

        "artificial intelligence",
        "machine learning",
        "generative ai",
        "generative artificial intelligence",
        "deep learning",


        # ----------------------------------------------------
        # GENERATIVE AI
        # ----------------------------------------------------

        "generative ai",
        "generative model",
        "generative models",
        "gan",
        "gans",
        "generative adversarial",
        "generative adversarial network",
        "vae",
        "vaes",
        "variational autoencoder",
        "variational autoencoders",
        "diffusion model",
        "diffusion models",


        # ----------------------------------------------------
        # LLM / TRANSFORMERS
        # ----------------------------------------------------

        "llm",
        "llms",
        "large language model",
        "large language models",
        "transformer",
        "transformers",
        "transformer architecture",
        "self attention",
        "self-attention",
        "attention mechanism",
        "attention mechanisms",
        "encoder",
        "decoder",
        "gpt",
        "bert",
        "palm",


        # ----------------------------------------------------
        # OTHER PDF TOPICS
        # ----------------------------------------------------

        "scaling",
        "llm scaling",
        "language model",
        "language models",
        "ai applications",
        "generative ai applications"
    ]


    # ========================================================
    # CHECK PDF KEYWORDS
    # ========================================================

    for keyword in pdf_keywords:

        if keyword in text:
            return "pdf"


    # ========================================================
    # DEFAULT
    # ========================================================

    return "none"