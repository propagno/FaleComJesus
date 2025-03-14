class BaseLLMService:
    """Base class for all LLM service implementations."""

    def __init__(self, api_key=None, cache=None):
        self.api_key = api_key
        self.cache = cache
        self._initialize()

    def _initialize(self):
        """Initialize the service. Should be implemented by subclasses."""
        pass

    def get_response(self, message, model=None, options=None):
        """Get a response from the LLM."""
        raise NotImplementedError("Subclasses must implement 'get_response'")

    def format_prompt(self, message, template=None, context=None):
        """
        Format the user message using a template if provided.

        Args:
            message (str): The user message
            template (str, optional): Template string to use for formatting
            context (dict, optional): Additional context variables for template

        Returns:
            str: Formatted message
        """
        if not template:
            # Default biblical assistant template
            template = """Você é um assistente espiritual cristão, baseado na Bíblia. Sua missão é fornecer orientação 
            e aconselhamento com base nos ensinamentos bíblicos. Responda à seguinte mensagem do usuário:
            
            {message}
            
            Inclua pelo menos uma referência bíblica relevante em sua resposta, citando o versículo.
            Mantenha sua resposta concisa, amorosa e respeitosa. Evite julgamentos.
            """

        # Prepare context dictionary
        ctx = {
            'message': message
        }

        # Add additional context if provided
        if context:
            ctx.update(context)

        # Use simple formatting
        try:
            return template.format(**ctx)
        except KeyError as e:
            # If format fails, log error and return original message
            logger.error(
                f"Template formatting error: {e}. Using default formatting.")
            return f"Responda à seguinte mensagem: {message}"
