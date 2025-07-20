import React, { useState, useEffect, createContext, useContext } from 'react';
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(userData);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(`${API}/auth/register`, userData);
      const { access_token, user: newUser } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(newUser);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Registration failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      login,
      register,
      logout,
      isAuthenticated: !!token && !!user
    }}>
      {children}
    </AuthContext.Provider>
  );
};

// Loading Component
const LoadingSpinner = () => (
  <div className="flex justify-center items-center min-h-screen">
    <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
  </div>
);

// Login Component
const LoginForm = ({ onToggleForm }) => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(formData.email, formData.password);
    
    if (!result.success) {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">Iniciar Sesión - ISTEM</h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            Email
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
            required
          />
        </div>
        
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            Contraseña
          </label>
          <input
            type="password"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
            required
          />
        </div>
        
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition duration-300 disabled:opacity-50"
        >
          {loading ? 'Ingresando...' : 'Iniciar Sesión'}
        </button>
      </form>
      
      <p className="mt-4 text-center">
        ¿No tienes cuenta?{' '}
        <button
          onClick={onToggleForm}
          className="text-blue-600 hover:text-blue-800 font-medium"
        >
          Regístrate aquí
        </button>
      </p>
    </div>
  );
};

// Register Component
const RegisterForm = ({ onToggleForm }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'student'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }

    if (formData.password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    setLoading(true);

    const result = await register({
      name: formData.name,
      email: formData.email,
      password: formData.password,
      role: formData.role
    });
    
    if (!result.success) {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">Registro - ISTEM</h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            Nombre Completo
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
            required
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            Email
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
            required
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            Rol
          </label>
          <select
            value={formData.role}
            onChange={(e) => setFormData({...formData, role: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
          >
            <option value="student">Estudiante</option>
            <option value="instructor">Instructor</option>
          </select>
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            Contraseña
          </label>
          <input
            type="password"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
            required
          />
        </div>
        
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            Confirmar Contraseña
          </label>
          <input
            type="password"
            value={formData.confirmPassword}
            onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
            required
          />
        </div>
        
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition duration-300 disabled:opacity-50"
        >
          {loading ? 'Registrando...' : 'Crear Cuenta'}
        </button>
      </form>
      
      <p className="mt-4 text-center">
        ¿Ya tienes cuenta?{' '}
        <button
          onClick={onToggleForm}
          className="text-blue-600 hover:text-blue-800 font-medium"
        >
          Inicia sesión aquí
        </button>
      </p>
    </div>
  );
};

// Hero Component
const Hero = () => (
  <div className="bg-gradient-to-r from-blue-600 to-purple-700 text-white py-20">
    <div className="container mx-auto px-4 text-center">
      <h1 className="text-5xl font-bold mb-6">
        Bienvenido a ISTEM
      </h1>
      <p className="text-xl mb-8 max-w-2xl mx-auto">
        La plataforma moderna de educación online. Aprende, progresa y alcanza tus metas académicas
        con nuestros cursos interactivos y reuniones virtuales.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto mt-12">
        <div className="text-center">
          <img 
            src="https://images.unsplash.com/photo-1541178735493-479c1a27ed24?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwxfHxvbmxpbmUlMjBlZHVjYXRpb258ZW58MHx8fGJsdWV8MTc1Mjk5MDU1N3ww&ixlib=rb-4.1.0&q=85"
            alt="Aprendizaje Online"
            className="w-64 h-48 object-cover rounded-lg mx-auto mb-4"
          />
          <h3 className="text-lg font-semibold">Aprendizaje Flexible</h3>
        </div>
        <div className="text-center">
          <img 
            src="https://images.unsplash.com/photo-1426024120108-99cc76989c71?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwyfHxvbmxpbmUlMjBlZHVjYXRpb258ZW58MHx8fGJsdWV8MTc1Mjk5MDU1N3ww&ixlib=rb-4.1.0&q=85"
            alt="Tecnología Educativa"
            className="w-64 h-48 object-cover rounded-lg mx-auto mb-4"
          />
          <h3 className="text-lg font-semibold">Tecnología Avanzada</h3>
        </div>
        <div className="text-center">
          <img 
            src="https://images.unsplash.com/photo-1651796704084-a115817945b2?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwzfHxvbmxpbmUlMjBlZHVjYXRpb258ZW58MHx8fGJsdWV8MTc1Mjk5MDU1N3ww&ixlib=rb-4.1.0&q=85"
            alt="Éxito Educativo"
            className="w-64 h-48 object-cover rounded-lg mx-auto mb-4"
          />
          <h3 className="text-lg font-semibold">Éxito Garantizado</h3>
        </div>
      </div>
    </div>
  </div>
);

// Dashboard Component
const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          ¡Hola, {user.name}! 👋
        </h1>
        <p className="text-gray-600">Bienvenido de vuelta a tu panel de aprendizaje</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
          <div className="flex items-center">
            <div className="p-3 bg-blue-500 rounded-full text-white mr-4">
              📚
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-700">Mis Cursos</h3>
              <p className="text-2xl font-bold text-blue-600">
                {dashboardData?.total_courses || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-green-50 p-6 rounded-lg border border-green-200">
          <div className="flex items-center">
            <div className="p-3 bg-green-500 rounded-full text-white mr-4">
              📊
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-700">Progreso Promedio</h3>
              <p className="text-2xl font-bold text-green-600">
                {dashboardData?.recent_courses?.length > 0 
                  ? Math.round(dashboardData.recent_courses.reduce((acc, c) => acc + c.progress, 0) / dashboardData.recent_courses.length)
                  : 0}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
          <div className="flex items-center">
            <div className="p-3 bg-purple-500 rounded-full text-white mr-4">
              🎥
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-700">Próximas Reuniones</h3>
              <p className="text-2xl font-bold text-purple-600">
                {dashboardData?.upcoming_meetings?.length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Courses */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Mis Cursos Recientes</h2>
        {dashboardData?.recent_courses?.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {dashboardData.recent_courses.map((courseData) => (
              <div key={courseData.course.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow">
                <div className="mb-2">
                  {courseData.course.thumbnail && (
                    <img 
                      src={courseData.course.thumbnail} 
                      alt={courseData.course.title}
                      className="w-full h-32 object-cover rounded-md mb-2"
                    />
                  )}
                  <h3 className="font-semibold text-gray-800">{courseData.course.title}</h3>
                  <p className="text-sm text-gray-600 mb-2">{courseData.course.description}</p>
                </div>
                
                <div className="mb-2">
                  <div className="flex justify-between items-center text-sm text-gray-600 mb-1">
                    <span>Progreso</span>
                    <span>{Math.round(courseData.progress)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${courseData.progress}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-500">
                    Instructor: {courseData.course.instructor_name}
                  </span>
                  <span className="text-blue-600 font-medium">{courseData.course.level}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p className="text-lg mb-2">¡Aún no tienes cursos!</p>
            <p>Explora nuestro catálogo y comienza a aprender hoy.</p>
          </div>
        )}
      </div>

      {/* Upcoming Meetings */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Próximas Reuniones Virtuales</h2>
        {dashboardData?.upcoming_meetings?.length > 0 ? (
          <div className="space-y-4">
            {dashboardData.upcoming_meetings.map((meeting) => (
              <div key={meeting.id} className="border border-gray-200 rounded-lg p-4 flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-gray-800">{meeting.title}</h3>
                  <p className="text-sm text-gray-600">{meeting.description}</p>
                  <p className="text-sm text-gray-500 mt-1">
                    📅 {new Date(meeting.scheduled_at).toLocaleDateString('es-ES', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
                <div>
                  <button 
                    onClick={() => window.open(meeting.meeting_url, '_blank')}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-300"
                  >
                    Unirse
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>No tienes reuniones programadas próximamente.</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Courses Component
const Courses = () => {
  const [courses, setCourses] = useState([]);
  const [myCourses, setMyCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('available');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [coursesResponse, myCoursesResponse] = await Promise.all([
        axios.get(`${API}/courses`),
        axios.get(`${API}/my-courses`)
      ]);
      
      setCourses(coursesResponse.data);
      setMyCourses(myCoursesResponse.data);
    } catch (error) {
      console.error('Error fetching courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const enrollInCourse = async (courseId) => {
    try {
      await axios.post(`${API}/enrollments/${courseId}`);
      alert('¡Te has inscrito exitosamente en el curso!');
      fetchData(); // Refresh data
    } catch (error) {
      alert(error.response?.data?.detail || 'Error al inscribirse en el curso');
    }
  };

  if (loading) return <LoadingSpinner />;

  const enrolledCourseIds = myCourses.map(mc => mc.course.id);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Catálogo de Cursos</h1>
      
      {/* Tab Navigation */}
      <div className="flex mb-8 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('available')}
          className={`px-6 py-3 font-medium ${
            activeTab === 'available' 
              ? 'text-blue-600 border-b-2 border-blue-600' 
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Cursos Disponibles ({courses.length})
        </button>
        <button
          onClick={() => setActiveTab('enrolled')}
          className={`px-6 py-3 font-medium ${
            activeTab === 'enrolled' 
              ? 'text-blue-600 border-b-2 border-blue-600' 
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Mis Cursos ({myCourses.length})
        </button>
      </div>

      {/* Available Courses Tab */}
      {activeTab === 'available' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <div key={course.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
              {course.thumbnail && (
                <img 
                  src={course.thumbnail} 
                  alt={course.title}
                  className="w-full h-48 object-cover"
                />
              )}
              <div className="p-6">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-semibold text-gray-800">{course.title}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    course.level === 'Beginner' ? 'bg-green-100 text-green-800' :
                    course.level === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {course.level}
                  </span>
                </div>
                
                <p className="text-gray-600 mb-4 text-sm">{course.description}</p>
                
                <div className="flex items-center justify-between mb-4 text-sm text-gray-500">
                  <span>👨‍🏫 {course.instructor_name}</span>
                  <span>⏱️ {course.duration_hours}h</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-lg font-bold text-blue-600">
                    {course.price > 0 ? `$${course.price}` : 'Gratis'}
                  </span>
                  
                  {enrolledCourseIds.includes(course.id) ? (
                    <span className="bg-green-100 text-green-800 px-4 py-2 rounded-md text-sm font-medium">
                      ✓ Inscrito
                    </span>
                  ) : (
                    <button
                      onClick={() => enrollInCourse(course.id)}
                      className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-300"
                    >
                      Inscribirse
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* My Courses Tab */}
      {activeTab === 'enrolled' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {myCourses.map((courseData) => (
            <div key={courseData.course.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
              {courseData.course.thumbnail && (
                <img 
                  src={courseData.course.thumbnail} 
                  alt={courseData.course.title}
                  className="w-full h-48 object-cover"
                />
              )}
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">{courseData.course.title}</h3>
                <p className="text-gray-600 mb-4 text-sm">{courseData.course.description}</p>
                
                <div className="mb-4">
                  <div className="flex justify-between items-center text-sm text-gray-600 mb-1">
                    <span>Progreso del Curso</span>
                    <span>{Math.round(courseData.enrollment.progress_percentage)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${courseData.enrollment.progress_percentage}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                  <span>👨‍🏫 {courseData.course.instructor_name}</span>
                  <span>📅 {new Date(courseData.enrollment.enrolled_at).toLocaleDateString('es-ES')}</span>
                </div>
                
                <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition duration-300">
                  Continuar Curso
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Empty States */}
      {activeTab === 'available' && courses.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">No hay cursos disponibles en este momento.</p>
        </div>
      )}
      
      {activeTab === 'enrolled' && myCourses.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg mb-2">Aún no estás inscrito en ningún curso.</p>
          <p>¡Explora nuestros cursos disponibles y comienza a aprender!</p>
          <button
            onClick={() => setActiveTab('available')}
            className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition duration-300"
          >
            Ver Cursos Disponibles
          </button>
        </div>
      )}
    </div>
  );
};

// Navigation Component
const Navigation = () => {
  const { user, logout } = useAuth();
  const [currentView, setCurrentView] = useState('dashboard');

  return (
    <>
      <nav className="bg-white shadow-md">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-8">
              <h1 className="text-2xl font-bold text-blue-600">ISTEM</h1>
              <div className="hidden md:flex space-x-6">
                <button
                  onClick={() => setCurrentView('dashboard')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'dashboard' 
                      ? 'bg-blue-100 text-blue-700' 
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  Panel Principal
                </button>
                <button
                  onClick={() => setCurrentView('courses')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === 'courses' 
                      ? 'bg-blue-100 text-blue-700' 
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  Cursos
                </button>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">¡Hola, {user.name}!</span>
              <button
                onClick={logout}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition duration-300"
              >
                Cerrar Sesión
              </button>
            </div>
          </div>
        </div>
      </nav>
      
      {/* Render current view */}
      <main>
        {currentView === 'dashboard' && <Dashboard />}
        {currentView === 'courses' && <Courses />}
      </main>
    </>
  );
};

// Public Layout (Login/Register)
const PublicLayout = () => {
  const [showLogin, setShowLogin] = useState(true);

  return (
    <div className="min-h-screen bg-gray-50">
      <Hero />
      <div className="container mx-auto px-4 py-8">
        {showLogin ? (
          <LoginForm onToggleForm={() => setShowLogin(false)} />
        ) : (
          <RegisterForm onToggleForm={() => setShowLogin(true)} />
        )}
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <div className="App">
        <AppContent />
      </div>
    </AuthProvider>
  );
}

const AppContent = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  return isAuthenticated ? <Navigation /> : <PublicLayout />;
};

export default App;