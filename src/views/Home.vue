<!-- src/views/Home.vue - Modern SaaS Design with Bulma/Buefy -->
<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero is-fullheight-with-navbar hero-gradient">
      <div class="hero-body">
        <div class="container">
          <div class="columns is-vcentered">
            <div class="column is-6">
              <span class="tag is-primary is-light is-medium mb-4">
                <b-icon icon="robot" size="is-small"></b-icon>
                <span class="ml-2">AI-Powered Solution</span>
              </span>
              <h1 class="title is-1 is-spaced has-text-weight-bold">
                Clean Your Data with
                <span class="has-text-success">AI Intelligence</span>
              </h1>
              <p class="subtitle is-4 has-text-white">
                Transform messy datasets into pristine, analysis-ready data in minutes.
                Our intelligent assistant guides you through every step.
              </p>
              
              <div class="buttons mt-5">
                <b-button
                  type="is-primary"
                  size="is-large"
                  rounded
                  @click="goGetStarted"
                  class="has-shadow-primary"
                >
                  <b-icon icon="rocket-launch"></b-icon>
                  <span>Start Free Trial</span>
                </b-button>
                <b-button
                  type="is-white"
                  size="is-large"
                  rounded
                  @click="watchDemo"
                >
                  <b-icon icon="play-circle"></b-icon>
                  <span>Watch Demo</span>
                </b-button>
              </div>

              <div class="trust-badges mt-5">
                <span class="is-size-7 has-text-grey">Trusted by data teams at</span>
                <div class="logos mt-2">
                  <span class="tag is-light">Fortune 500</span>
                  <span class="tag is-light">Startups</span>
                  <span class="tag is-light">Research Labs</span>
                </div>
              </div>
            </div>
            
            <div class="column is-6">
              <div class="hero-visual">
                <div class="dashboard-preview">
                  <div class="window-header">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                  </div>
                  <div class="window-content">
                    <div class="data-flow">
                      <div class="data-block dirty">
                        <b-icon icon="file-alert" type="is-danger"></b-icon>
                        <span>Messy Data</span>
                      </div>
                      <b-icon icon="arrow-right" size="is-large" type="is-primary"></b-icon>
                      <div class="data-block clean">
                        <b-icon icon="file-check" type="is-success"></b-icon>
                        <span>Clean Data</span>
                      </div>
                    </div>
                    <div class="stats-preview">
                      <div class="stat-item">
                        <span class="stat-value">98%</span>
                        <span class="stat-label">Accuracy</span>
                      </div>
                      <div class="stat-item">
                        <span class="stat-value">10x</span>
                        <span class="stat-label">Faster</span>
                      </div>
                      <div class="stat-item">
                        <span class="stat-value">0</span>
                        <span class="stat-label">Errors</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Key Features Section -->
    <section class="section is-medium">
      <div class="container">
        <div class="has-text-centered mb-6">
          <h2 class="title is-2 has-text-weight-bold">Why Teams Choose MasterDataCleaner</h2>
          <p class="subtitle is-5 has-text-grey">
            Powerful features designed for modern data workflows
          </p>
        </div>

        <div class="columns is-multiline">
          <div class="column is-4">
            <div class="feature-box">
              <div class="feature-icon">
                <b-icon icon="brain" type="is-primary" size="is-large"></b-icon>
              </div>
              <h3 class="title is-5">AI-Guided Cleaning</h3>
              <p class="has-text-grey">
                Smart suggestions for deduplication, normalization, and outlier detection.
                Our AI learns from your decisions.
              </p>
              <a class="feature-link">Learn more →</a>
            </div>
          </div>

          <div class="column is-4">
            <div class="feature-box">
              <div class="feature-icon">
                <b-icon icon="lightning-bolt" type="is-warning" size="is-large"></b-icon>
              </div>
              <h3 class="title is-5">Lightning Fast</h3>
              <p class="has-text-grey">
                Process millions of rows in seconds. Our optimized engine handles
                datasets of any size without breaking a sweat.
              </p>
              <a class="feature-link">See benchmarks →</a>
            </div>
          </div>

          <div class="column is-4">
            <div class="feature-box">
              <div class="feature-icon">
                <b-icon icon="shield-check" type="is-success" size="is-large"></b-icon>
              </div>
              <h3 class="title is-5">Enterprise Ready</h3>
              <p class="has-text-grey">
                SOC 2 compliant with end-to-end encryption. Your data never leaves
                your infrastructure.
              </p>
              <a class="feature-link">Security details →</a>
            </div>
          </div>

          <div class="column is-4">
            <div class="feature-box">
              <div class="feature-icon">
                <b-icon icon="database-export" type="is-info" size="is-large"></b-icon>
              </div>
              <h3 class="title is-5">Universal Export</h3>
              <p class="has-text-grey">
                Export to any database or file format. Native integrations with
                PostgreSQL, MySQL, CSV, JSON, and Parquet.
              </p>
              <a class="feature-link">View integrations →</a>
            </div>
          </div>

          <div class="column is-4">
            <div class="feature-box">
              <div class="feature-icon">
                <b-icon icon="code-braces" type="is-danger" size="is-large"></b-icon>
              </div>
              <h3 class="title is-5">Custom Scripts</h3>
              <p class="has-text-grey">
                Extend with Python or JavaScript. Build custom transformations
                and automate repetitive workflows.
              </p>
              <a class="feature-link">API docs →</a>
            </div>
          </div>

          <div class="column is-4">
            <div class="feature-box">
              <div class="feature-icon">
                <b-icon icon="history" type="is-link" size="is-large"></b-icon>
              </div>
              <h3 class="title is-5">Version Control</h3>
              <p class="has-text-grey">
                Track every change with full audit trails. Rollback mistakes
                instantly with time-travel debugging.
              </p>
              <a class="feature-link">How it works →</a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="section is-medium has-background-light">
      <div class="container">
        <div class="has-text-centered mb-6">
          <h2 class="title is-2 has-text-weight-bold">Simple 4-Step Process</h2>
          <p class="subtitle is-5 has-text-grey">
            From messy data to production-ready in minutes
          </p>
        </div>

        <div class="process-timeline">
          <div class="columns">
            <div class="column is-3">
              <div class="process-step">
                <div class="step-number">1</div>
                <h4 class="title is-6">Connect</h4>
                <p class="is-size-7 has-text-grey">
                  Import from databases, APIs, or upload files directly
                </p>
              </div>
            </div>
            <div class="column is-3">
              <div class="process-step">
                <div class="step-number">2</div>
                <h4 class="title is-6">Analyze</h4>
                <p class="is-size-7 has-text-grey">
                  AI scans for issues and suggests cleaning strategies
                </p>
              </div>
            </div>
            <div class="column is-3">
              <div class="process-step">
                <div class="step-number">3</div>
                <h4 class="title is-6">Clean</h4>
                <p class="is-size-7 has-text-grey">
                  Apply transformations with real-time preview
                </p>
              </div>
            </div>
            <div class="column is-3">
              <div class="process-step">
                <div class="step-number">4</div>
                <h4 class="title is-6">Export</h4>
                <p class="is-size-7 has-text-grey">
                  Push clean data to your destination of choice
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Metrics Section -->
    <section class="section is-medium">
      <div class="container">
        <div class="box metrics-box">
          <div class="columns is-vcentered">
            <div class="column is-5">
              <h3 class="title is-3 has-text-weight-bold">
                Trusted by 10,000+ data professionals
              </h3>
              <p class="subtitle is-6 has-text-grey mt-3">
                Join thousands of companies that rely on MasterDataCleaner
                to maintain data quality at scale.
              </p>
              <b-button type="is-primary" rounded class="mt-4" @click="goGetStarted">
                Get Started Free
              </b-button>
            </div>
            <div class="column is-7">
              <div class="columns is-multiline">
                <div class="column is-6">
                  <div class="metric-item">
                    <span class="metric-value">500M+</span>
                    <span class="metric-label">Records Cleaned</span>
                  </div>
                </div>
                <div class="column is-6">
                  <div class="metric-item">
                    <span class="metric-value">99.9%</span>
                    <span class="metric-label">Uptime SLA</span>
                  </div>
                </div>
                <div class="column is-6">
                  <div class="metric-item">
                    <span class="metric-value">85%</span>
                    <span class="metric-label">Time Saved</span>
                  </div>
                </div>
                <div class="column is-6">
                  <div class="metric-item">
                    <span class="metric-value">24/7</span>
                    <span class="metric-label">Support</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="section is-medium cta-section">
      <div class="container">
        <div class="has-text-centered">
          <h2 class="title is-2 has-text-white has-text-weight-bold">
            Ready to transform your data?
          </h2>
          <p class="subtitle is-5 has-text-white-ter mt-3">
            Start your free trial today. No credit card required.
          </p>
          <div class="buttons is-centered mt-5">
            <b-button
              type="is-white"
              size="is-large"
              rounded
              @click="goGetStarted"
            >
              <b-icon icon="rocket-launch"></b-icon>
              <span>Start Free Trial</span>
            </b-button>
            <b-button
              type="is-primary"
              inverted
              outlined
              size="is-large"
              rounded
              @click="contactSales"
            >
              <span>Contact Sales</span>
            </b-button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goGetStarted = () => {
  router.push('/connections').catch(() => {})
}

const watchDemo = () => {
  window.open('https://www.youtube.com/watch?v=demo', '_blank')
}

const contactSales = () => {
  window.open('mailto:sales@masterdatacleaner.com', '_blank')
}
</script>

<style scoped>
.home-page {
  overflow-x: hidden;
}

/* Hero Section */
.hero-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.hero-gradient::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 20% 80%, rgba(255,255,255,0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 50%);
}

.hero-gradient .title,
.hero-gradient .subtitle {
  color: white;
}

.has-shadow-primary {
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
}

.trust-badges .logos {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Dashboard Preview */
.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
}

.dashboard-preview {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  overflow: hidden;
  width: 100%;
  max-width: 500px;
}

.window-header {
  background: #f5f5f5;
  padding: 12px;
  display: flex;
  gap: 6px;
}

.window-header .dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ddd;
}

.window-header .dot:first-child { background: #ff5f57; }
.window-header .dot:nth-child(2) { background: #ffbd2e; }
.window-header .dot:nth-child(3) { background: #28ca42; }

.window-content {
  padding: 2rem;
}

.data-flow {
  display: flex;
  align-items: center;
  justify-content: space-around;
  margin-bottom: 2rem;
}

.data-block {
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.data-block.dirty {
  background: #ffe5e5;
}

.data-block.clean {
  background: #e5ffe5;
}

.stats-preview {
  display: flex;
  justify-content: space-around;
  padding-top: 1rem;
  border-top: 1px solid #f0f0f0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #667eea;
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: #999;
}

/* Feature Boxes */
.feature-box {
  padding: 2rem;
  height: 100%;
  transition: transform 0.3s, box-shadow 0.3s;
  border-radius: 12px;
  background: white;
  border: 1px solid #f0f0f0;
}

.feature-box:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.1);
}

.feature-icon {
  margin-bottom: 1.5rem;
}

.feature-link {
  color: #667eea;
  font-size: 0.9rem;
  font-weight: 500;
  display: inline-block;
  margin-top: 1rem;
}

.feature-link:hover {
  text-decoration: underline;
}

/* Process Timeline */
.process-timeline {
  position: relative;
  margin-top: 3rem;
}

.process-timeline::before {
  content: '';
  position: absolute;
  top: 30px;
  left: 12.5%;
  right: 12.5%;
  height: 2px;
  background: linear-gradient(to right, #667eea, #764ba2);
}

.process-step {
  text-align: center;
  position: relative;
}

.step-number {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0 auto 1rem;
  position: relative;
  z-index: 1;
}

/* Metrics */
.metrics-box {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border: none;
  padding: 3rem;
}

.metric-item {
  text-align: center;
  padding: 1.5rem;
}

.metric-value {
  display: block;
  font-size: 2.5rem;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.metric-label {
  display: block;
  font-size: 0.9rem;
  color: #666;
  margin-top: 0.5rem;
}

/* CTA Section */
.cta-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.cta-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

/* Responsive */
@media (max-width: 768px) {
  .hero-visual {
    margin-top: 3rem;
  }
  
  .process-timeline::before {
    display: none;
  }
  
  .metrics-box {
    padding: 2rem 1rem;
  }
}
</style>