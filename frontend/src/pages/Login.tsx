import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Logo } from '@/components/ui/logo';
import { useAuthStore } from '@/stores/authStore';
import api from '@/lib/api';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';
import { User } from '@/types';

export default function Login() {
  const navigate = useNavigate();
  const { setUser } = useAuthStore();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('grant_type', 'password');
      formData.append('username', username);
      formData.append('password', password);

      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        validateStatus: (status) => status < 500, // <- prevents axios auto-throw for 4xx
      });

      if (response.status === 401 && response.data.detail === 'User not found') {
        toast.error('User not registered yet. Please sign up to continue.', {
          action: {
            label: 'Sign up',
            onClick: () => navigate('/register'),
          },
        });
        return;
      } else if (response.status === 401 && response.data.detail === 'Invalid credentials') {
        toast.error('Invalid password. Please try again.');
        return;
      }

      if (response.data.status !== 'success') {
        toast.error(response.data.message || 'Login failed');
        return;
      }

      const { access_token, refresh_token } = response.data.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      const userResponse = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` },
      });

      const userData = userResponse.data.data;
      const user: User = {
        id: userData.id,
        email: userData.email,
        first_name: userData.firstname,
        last_name: userData.lastname,
      };

      setUser(user);
      toast.success(`Welcome back, ${user.first_name || user.email}!`);
      navigate('/dashboard');
    } catch (error: any) {
      toast.error(
        error.response?.data?.detail ||
        error.response?.data?.message ||
        'Login failed'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-primary/5 p-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="space-y-4 text-center">
          <div className="flex justify-center">
            <Link to="/" className="hover:opacity-80 transition-opacity">
              <Logo className="scale-125" />
            </Link>
          </div>
          <CardTitle className="text-2xl">Welcome Back</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Email</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter your email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
            <Button
              type="submit"
              className="w-full ai-gradient"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex flex-col gap-2">
          <p className="text-sm text-muted-foreground">
            Don't have an account?{' '}
            <Link
              to="/register"
              className="text-primary hover:underline font-medium"
            >
              Sign up
            </Link>
          </p>
          <Link
            to="/"
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            ← Back to Home
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}
