import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import styles from './index.module.css';

export default function Home() {
  return (
    <Layout title="CoPipes" description="Collaborative ETL and data analysis platform">
      <header className={styles.heroBanner}>
        <div className="container">
          <h1 className={styles.title}>CoPipes</h1>
          <p className={styles.subtitle}>Build, Share, and Automate Your Data Workflows Collaboratively</p>
          {/* <Link className="button button--primary button--lg" to="/docs/intro">
            Get Started
          </Link> */}
        </div>
      </header>

      <main>
        <section className={styles.features}>
          <div className="container">
            <div className="row">
              {features.map(({ title, description }, idx) => (
                <div key={idx} className="col col--4 margin-bottom--lg">
                  <div className={styles.featureCard}>
                    <h3>{title}</h3>
                    <p>{description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}

const features = [
  {
    title: 'Collaborative workflow builder',
    description: 'Design ETL pipelines visually with team support using linear or graph views.',
  },
  {
    title: 'Plug-and-play tasks',
    description: 'Choose from a library of pre-built tasks or build your own reusable components.',
  },
  {
    title: 'Apache Airflow powered',
    description: 'Orchestrate and monitor workflows with scalable Airflow integration.',
  },
  {
    title: 'FastAPI backend',
    description: 'Use a clean, modern API to extend workflows, users, and datasets.',
  },
  {
    title: 'Post-ETL analysis',
    description: 'Run AI/ML models on cleaned data directly in the platform.',
  },
  {
    title: 'Customizable & open source',
    description: 'Easily extend and contribute to the system. Made for research and collaboration.',
  },
];
