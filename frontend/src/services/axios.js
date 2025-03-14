import axios from 'axios';

// Cria uma instância do Axios com configurações padrão
const axiosInstance = axios.create({
  baseURL: '', // Deixando vazio para usar o proxy do React
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
});

// Interceptor para adicionar token de autenticação às requisições
axiosInstance.interceptors.request.use(
  config => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      console.log('Adding token to request:', config.url);
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.log('No token available for request:', config.url);
    }
    return config;
  },
  error => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Interceptor para lidar com erros de resposta (como token expirado)
axiosInstance.interceptors.response.use(
  response => {
    console.log('Response received for:', response.config.url);
    return response;
  },
  async error => {
    console.error('Response error:', error.config?.url, error.message);
    
    const originalRequest = error.config;
    
    // Se o erro for 401 (não autorizado) e ainda não tentamos refazer a requisição
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Tenta obter um novo token usando o refreshToken
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          console.log('Attempting to refresh token...');
          const res = await axios.post('/api/v1/auth/refresh', {}, {
            headers: {
              'Authorization': `Bearer ${refreshToken}`
            }
          });
          
          // Atualiza os tokens no localStorage
          const newToken = res.data.access_token;
          console.log('New token received:', newToken ? 'Yes' : 'No');
          localStorage.setItem('accessToken', newToken);
          
          // Atualiza o header da requisição original e a refaz
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return axiosInstance(originalRequest);
        }
      } catch (err) {
        console.error('Erro ao renovar token:', err);
        // Se falhar ao obter novo token, limpa o localStorage e redireciona para login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        
        // Redireciona para a página de login (isso deve ser tratado em um contexto React)
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export default axiosInstance; 