
import { motion } from 'framer-motion';
import { Mic, Link2, Zap, MessageSquare, Smartphone, Layers } from 'lucide-react';
import React from 'react';
import styles from './Features.module.css';

export const features = [
    {
        icon: Mic,
        title: 'Voice-Powered Intelligence',
        description: 'Simply speak naturally - SAM understands context and intent to deliver exactly what you want to hear.',
        color1: '#7c3aed', color2: '#ec4899',
    },
    {
        icon: Link2,
        title: 'Universal Platform Access',
        description: 'Seamlessly works across Spotify, Apple Music, Amazon Music, SoundCloud and more - all in one place.',
        color1: '#2563eb', color2: '#06b6d4',
    },
    {
        icon: Zap,
        title: 'Seamless Integration',
        description: 'Unified control across all your music services. Switch between platforms effortlessly without missing a beat.',
        color1: '#06b6d4', color2: '#14b8a6',
    },
    {
        icon: MessageSquare,
        title: 'Context-Aware',
        description: 'SAM remembers what you just said. Ask follow-up questions or refine your requests naturally without repeating details.',
        color1: '#ec4899', color2: '#9333ea',
    },
    {
        icon: Smartphone,
        title: 'Real-Time Sync',
        description: 'Your music, playlists, and preferences sync instantly across all your devices - phone, tablet, desktop, and smart speakers.',
        color1: '#f97316', color2: '#ec4899',
    },
    {
        icon: Layers,
        title: 'Multi-Action Handling',
        description: 'Handle multi-step requests in a single breath. "Play Blinding Lights and add it to my Gym playlist" works instantly.',
        color1: '#f59e0b', color2: '#d97706',
    },
];

export const FeatureCard = ({ feature, index: _index, is3D = false }: { feature: any, index: number, is3D?: boolean }) => {
    const [hovered, setHovered] = React.useState(false);

    return (
        <motion.div
            initial={is3D ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
            whileInView={is3D ? undefined : { opacity: 1, y: 0 }}
            viewport={is3D ? undefined : { once: true }}
            transition={{ duration: 0.5, delay: 0.04 }}
            onHoverStart={() => setHovered(true)}
            onHoverEnd={() => setHovered(false)}
            data-hovered={hovered}
            animate={{
                y: hovered ? -15 : 0,
                scale: hovered ? 1.15 : 1,
                rotateX: hovered ? 5 : 0,
                rotateY: hovered ? 5 : 0,
            }}
            className={styles.featureCard}
            style={{
                /* Dynamic Shadow / Glow - INTENSE NEON BLOOM */
                boxShadow: hovered
                    ? `
                        0 20px 60px ${feature.color1}60, 
                        0 0 30px ${feature.color1}40, 
                        0 0 0 2px ${feature.color1}
                      `
                    : '0 10px 30px rgba(0,0,0,0.2)',
                width: '100%',
                height: '100%',
                // @ts-ignore
                '--color-1': feature.color1,
                '--color-2': feature.color2,
            }}
        >
            <div
                className={styles.iconContainer}
                style={{
                    // Keeping inline for gradient with specific start/end colors and alpha shadow
                    background: `linear-gradient(135deg, ${feature.color1}, ${feature.color2})`,
                    boxShadow: `0 8px 20px ${feature.color1}50`,
                }}
            >
                <feature.icon size={28} color="white" strokeWidth={2.5} />
            </div>

            <h3
                className={styles.cardTitle}
                style={{
                    textShadow: hovered ? `0 0 20px ${feature.color1}80` : 'none',
                }}
            >
                {feature.title}
            </h3>

            <p className={styles.cardDescription}>
                {feature.description}
            </p>

            <div className={styles.bottomGlow} />
        </motion.div>
    );
};
