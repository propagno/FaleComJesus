# Fale Com Jesus - Assistente Bíblico

Uma aplicação web que oferece orientação espiritual e aconselhamento baseado na Bíblia, utilizando tecnologias modernas de IA.

## 🌟 Funcionalidades

- **Chat com IA Bíblica**: Converse com um assistente virtual que responde com orientações baseadas na Bíblia
- **Mensagem do Dia**: Receba uma mensagem inspiradora diária com versículo bíblico
- **Anotações Pessoais**: Registre suas reflexões e pensamentos
- **Múltiplos Provedores de IA**: Suporte para OpenAI, Google, Anthropic e Mistral
- **Personalização de Prompts**: Crie e gerencie templates para personalizar as respostas
- **Gerenciamento de Conversas**: Salve, organize e exporte suas conversas
- **Autenticação Segura**: Login com e-mail/senha e OAuth

## 🛠️ Tecnologias Utilizadas

### Frontend
- React (SPA)
- Material-UI
- Context API para gerenciamento de estado
- React Router para navegação

### Backend
- Flask (Microserviços)
- SQLAlchemy ORM
- JWT para autenticação
- Marshmallow para validação

### Banco de Dados e Cache
- PostgreSQL
- Redis para cache

### Mensageria e Monitoramento
- RabbitMQ para filas de mensagens
- Elastic Stack para logs e monitoramento

### Infraestrutura
- Docker e Docker Compose
- Ambientes de desenvolvimento e produção

## 📋 Requisitos

- Node.js 16+
- Python 3.9+
- Docker e Docker Compose
- PostgreSQL 13+
- Redis 6+

## 🚀 Instalação e Execução

### Configuração do Ambiente

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/fale-com-jesus.git
cd fale-com-jesus
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### Backend

1. Crie e ative um ambiente virtual Python:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

2. Instale as dependências:
```bash
cd backend
pip install -r requirements.txt
```

3. Execute as migrações:
```bash
python migrations/run_migrations.py
```

4. Inicie o servidor:
```bash
python run.py
```

### Frontend

1. Instale as dependências:
```bash
cd frontend
npm install
```

2. Inicie o servidor de desenvolvimento:
```bash
npm start
```

### Docker (Opcional)

Para executar toda a aplicação com Docker:

```bash
docker-compose up -d
```

## 🧪 Testes

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

### End-to-End
```bash
cd tests/e2e
npx playwright test
```

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Contribuição

Contribuições são bem-vindas! Por favor, leia as [diretrizes de contribuição](CONTRIBUTING.md) antes de enviar um pull request.

## 📞 Contato

Para dúvidas ou sugestões, entre em contato através de [seu-email@exemplo.com](mailto:seu-email@exemplo.com). 