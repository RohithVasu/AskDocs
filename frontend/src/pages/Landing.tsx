import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Logo } from '@/components/ui/logo';
import { useTheme } from 'next-themes';
import {
    FileText,
    MessageSquare,
    Search,
    Target,
    Moon,
    Sun,
    ArrowRight,
} from 'lucide-react';
import { motion } from 'framer-motion';

export default function Landing() {
    const navigate = useNavigate();
    const { isAuthenticated } = useAuthStore();
    const { theme, setTheme } = useTheme();

    // Redirect authenticated users to dashboard
    useEffect(() => {
        if (isAuthenticated) {
            navigate('/dashboard');
        }
    }, [isAuthenticated, navigate]);

    const features = [
        {
            icon: FileText,
            title: 'Document Upload & Management',
            description: 'Easily upload and organize your documents in one centralized location.',
        },
        {
            icon: MessageSquare,
            title: 'AI-Powered Chat Interface',
            description: 'Engage in natural conversations with your documents using advanced AI.',
        },
        {
            icon: Search,
            title: 'Intelligent Document Search',
            description: 'Find relevant information instantly with smart semantic search.',
        },
        {
            icon: Target,
            title: 'Context-Aware Responses',
            description: 'Get accurate answers grounded in your document content.',
        },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
            {/* Header */}
            <header className="border-b backdrop-blur-sm bg-background/80 sticky top-0 z-50">
                <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                        <Logo className="scale-110" />
                    </Link>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
                            className="rounded-full"
                        >
                            {theme === 'light' ? (
                                <Moon className="h-5 w-5" />
                            ) : (
                                <Sun className="h-5 w-5" />
                            )}
                        </Button>
                        <Button variant="ghost" onClick={() => navigate('/login')}>
                            Login
                        </Button>
                        <Button className="ai-gradient" onClick={() => navigate('/register')}>
                            Get Started
                        </Button>
                    </div>
                </div>
            </header>

            {/* Hero Section */}
            <section className="container mx-auto px-4 py-20 md:py-32">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="text-center max-w-4xl mx-auto"
                >
                    <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                        Chat with Your Documents
                        <br />
                        <span className="bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
                            Using AI
                        </span>
                    </h1>
                    <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
                        Transform how you interact with your documents. Upload, search, and get intelligent answers
                        from your files using cutting-edge AI technology.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <Button
                            size="lg"
                            className="ai-gradient text-lg px-8"
                            onClick={() => navigate('/register')}
                        >
                            Try Now
                            <ArrowRight className="ml-2 h-5 w-5" />
                        </Button>
                        <Button
                            size="lg"
                            variant="outline"
                            className="text-lg px-8"
                            onClick={() => navigate('/login')}
                        >
                            Sign In
                        </Button>
                    </div>
                </motion.div>
            </section>

            {/* Features Section */}
            <section className="container mx-auto px-4 py-20 md:py-32">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-3xl md:text-4xl font-bold mb-4">
                        Everything You Need
                    </h2>
                    <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                        Powerful features designed to make document interaction seamless and intuitive.
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {features.map((feature, index) => (
                        <motion.div
                            key={feature.title}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: 0.1 * index }}
                        >
                            <Card className="h-full hover:shadow-lg transition-shadow border-border/50">
                                <CardContent className="p-6">
                                    <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                                        <feature.icon className="h-6 w-6 text-primary" />
                                    </div>
                                    <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                                    <p className="text-muted-foreground text-sm">
                                        {feature.description}
                                    </p>
                                </CardContent>
                            </Card>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* CTA Section */}
            <section className="container mx-auto px-4 py-20 md:py-32">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                    className="text-center max-w-3xl mx-auto"
                >
                    <Card className="border-primary/20 shadow-xl">
                        <CardContent className="p-12">
                            <h2 className="text-3xl md:text-4xl font-bold mb-4">
                                Ready to Get Started?
                            </h2>
                            <p className="text-lg text-muted-foreground mb-8">
                                Join AskDocs today and revolutionize how you work with documents.
                            </p>
                            <div className="flex flex-col sm:flex-row gap-4 justify-center">
                                <Button
                                    size="lg"
                                    className="ai-gradient text-lg px-8"
                                    onClick={() => navigate('/register')}
                                >
                                    Create Account
                                    <ArrowRight className="ml-2 h-5 w-5" />
                                </Button>
                                <Button
                                    size="lg"
                                    variant="outline"
                                    className="text-lg px-8"
                                    onClick={() => navigate('/login')}
                                >
                                    Sign In
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>
            </section>

            {/* Footer */}
            <footer className="border-t py-8">
                <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
                    <p>&copy; 2025 AskDocs. All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
}
