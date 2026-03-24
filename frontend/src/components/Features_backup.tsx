
import { motion } from 'framer-motion';
import React, { Suspense } from 'react';
import styles from './Features.module.css';
import FeaturesCube from './FeaturesCube';

// Lazy load the heavy 3D background component
const FeaturesBackground = React.lazy(() => import('./FeaturesBackground'));

const Features = () => {
    return (
        <section id="features" className={styles.featuresSection}>
            {/* 3D Background - HeroParticles */}
            {/* 3D Background - Lazy Loaded with Fade-In */}
            <Suspense fallback={null}>
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 1.5, ease: "easeOut" }} // Smooth cinematic fade-in
                    className={styles.backgroundContainer}
                >
                    <FeaturesBackground />
                </motion.div>
            </Suspense>

            {/* Content Container */}
            <div className={styles.contentContainer}>
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className={styles.headerWrapper}
                >
                    <h2 className={`text-gradient ${styles.title}`}>
                        Powerful Features
                    </h2>
                    <p className={styles.description}>
                        Effortlessly command, curate, and synchronize your entire music universe using just your voice.
                    </p>
                </motion.div>

                {/* 3D Cube Presentation */}
                <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '4rem' }}>
                    <FeaturesCube />
                </div>

                {/* --- Platform Capabilities Section --- */}
                <motion.div
                    id="platform-intelligence"
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className={styles.platformSection}
                >
                    <h2 className={`text-gradient ${styles.platformTitle}`}>
                        Platform Intelligence
                    </h2>

                    <div className={styles.platformGrid}>
                        {/* Spotify Card */}
                        <CapabilityCard
                            platform="Spotify"
                            color="#1DB954"
                            capabilities={SPOTIFY_CAPABILITIES}
                        />

                        {/* SoundCloud Card */}
                        <CapabilityCard
                            platform="SoundCloud"
                            color="#ff5500"
                            capabilities={SOUNDCLOUD_CAPABILITIES}
                        />
                    </div>
                </motion.div>
            </div>
        </section>
    );
};

const SPOTIFY_CAPABILITIES = [
    "Playback Control: Play, Pause, Resume, Next, Previous",
    "Precision Seeking: Jump to any specific timestamp",
    "Smart Play: 'Play [Song] by [Artist]'",
    "Play your 'Liked Songs' collection",
    "Playlist Management: Create, Delete, & Rename playlists",
    "Curate: Add or Remove tracks from any playlist",
    "Organize: Reorder tracks within your playlists",
    "Library: Like / Unlike the current song instantly",
    "Context Aware: Controls active Spotify Connect devices"
];

const SOUNDCLOUD_CAPABILITIES = [
    "Search: Find untagged/remix tracks in the full catalog",
    "Playback: Stream tracks via the visual widget",
    "Playlist Creation: Create new public playlists",
    "Playlist Editing: Delete playlists & clear tracks",
    "Curate: Add any track to your playlists",
    "Favorites: Like / Unlike tracks to your library",
    "Library: Access your full Liked Tracks history",
    "Import: Syncs your existing personal playlists",
    "Metadata: View detailed track/artist info"
];

const CapabilityCard = ({ platform, color, capabilities }: { platform: string, color: string, capabilities: string[] }) => {
    return (
        <div
            className={styles.capabilityCard}
            style={{
                // @ts-ignore
                '--cap-color': color,
                '--cap-border-color': `${color}20`,
                '--cap-bg-weak': `${color}15`,
                '--cap-border-weak': `${color}40`,
            }}
        >
            {/* Header / Logo Area */}
            <div className={styles.cardHeader}>
                <div className={styles.platformDot} />
                <h3 className={styles.platformName}>{platform}</h3>
            </div>

            {/* List */}
            <ul className={styles.capabilityList}>
                {capabilities.map((cap, i) => (
                    <li key={i} className={styles.capabilityItem}>
                        {/* Check Icon */}
                        <div className={styles.checkIcon}>✓</div>
                        <span className={styles.capabilityText}>{cap}</span>
                    </li>
                ))}
            </ul>

            {/* Bottom Glow */}
            <div className={styles.cardGlow} />
        </div>
    );
};

export default Features;
