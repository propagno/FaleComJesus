from app.models.prompt_template import PromptTemplate
from app.utils.logger import logger


def get_template_by_id(template_id):
    """
    Obtém um template de prompt pelo ID
    """
    return PromptTemplate.query.get(template_id)


def get_system_templates():
    """
    Obtém todos os templates de sistema
    """
    return PromptTemplate.query.filter_by(is_system=True).all()


def get_user_templates(user_id):
    """
    Obtém todos os templates de um usuário específico
    """
    return PromptTemplate.query.filter_by(user_id=user_id).all()


def get_available_templates(user_id):
    """
    Obtém todos os templates disponíveis para um usuário (sistema + próprios)
    """
    system_templates = get_system_templates()
    user_templates = get_user_templates(user_id)
    return system_templates + user_templates


def format_prompt(template_text, message, context=None):
    """
    Formata um prompt usando um template

    Args:
        template_text (str): Texto do template
        message (str): Mensagem do usuário
        context (dict, optional): Contexto adicional

    Returns:
        str: Prompt formatado
    """
    try:
        # Preparar contexto
        ctx = {
            'message': message
        }

        # Adicionar contexto adicional se fornecido
        if context:
            ctx.update(context)

        # Formatar usando string.format()
        return template_text.format(**ctx)
    except Exception as e:
        logger.error(f"Erro ao formatar prompt: {str(e)}")
        # Fallback para formato simples
        return f"Responda à seguinte mensagem: {message}"
