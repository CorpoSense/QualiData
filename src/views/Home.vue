<!-- src/views/Home.vue - Modern SaaS Redesign with Buefy 3.0.4 -->
<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero is-medium is-bold is-relative overflow-hidden">
      <div class="hero-background-pattern"></div>
      <div class="hero-body">
        <div class="container">
          <div class="columns is-vcentered">
            <div class="column is-6 animate-fade-in-left">
              <b-tag
                type="is-primary"
                rounded
                size="is-medium"
                class="mb-4 glow-tag"
              >
                <b-icon icon="sparkles" size="is-small" class="mr-1"></b-icon>
                Version 3.0 is here
              </b-tag>
              <h1 class="title is-1 is-spaced has-text-weight-black">
                Master Your Data with
                <span class="gradient-text">AI Precision</span>
              </h1>
              <p class="subtitle is-4 has-text-grey-darker mb-6">
                The ultimate platform for cleaning, normalizing, and enriching your master data. 
                Say goodbye to manual spreadsheets and hello to automated intelligence.
              </p>
              
              <div class="buttons">
                <b-button
                  type="is-primary"
                  size="is-large"
                  rounded
                  class="px-6 py-4 has-text-weight-bold"
                  @click="goGetStarted"
                >
                  Get Started Free
                </b-button>
                <b-button
                  type="is-white"
                  size="is-large"
                  rounded
                  outlined
                  class="px-6 py-4 has-text-weight-bold"
                  @click="watchDemo"
                >
                  <b-icon icon="play" class="mr-2"></b-icon>
                  Watch Demo
                </b-button>
              </div>

              <div class="mt-6 flex align-center">
                <div class="avatar-group mr-4">
                  <img src="https://i.pravatar.cc/150?u=1" alt="User" class="avatar">
                  <img src="https://i.pravatar.cc/150?u=2" alt="User" class="avatar">
                  <img src="https://i.pravatar.cc/150?u=3" alt="User" class="avatar">
                  <div class="avatar-more">+2k</div>
                </div>
                <p class="is-size-7 has-text-grey-dark">
                  Joined by <strong>2,000+</strong> data engineers this month.
                </p>
              </div>
            </div>
            
            <div class="column is-6 animate-fade-in-right">
              <div class="hero-card-container">
                <div class="glass-card main-preview">
                  <div class="card-header-mock">
                    <div class="window-dots">
                      <span></span><span></span><span></span>
                    </div>
                    <div class="search-bar-mock">master-data-cleanup.csv</div>
                  </div>
                  <div class="card-content">
                    <div class="data-cleaning-animation">
                      <div class="data-row dirty-row">
                        <div class="cell-mock">Jhn Doe</div>
                        <div class="cell-mock">ny, usa</div>
                        <div class="cell-mock danger">invalid_email</div>
                      </div>
                      <div class="cleaning-line"></div>
                      <div class="data-row clean-row">
                        <div class="cell-mock">John Doe</div>
                        <div class="cell-mock">New York, USA</div>
                        <div class="cell-mock success">john@example.com</div>
                      </div>
                    </div>
                    <div class="metrics-row mt-4">
                      <div class="metric-small">
                        <p class="label">Accuracy</p>
                        <p class="value has-text-success">99.9%</p>
                      </div>
                      <div class="metric-small">
                        <p class="label">Duplicates</p>
                        <p class="value has-text-danger">0</p>
                      </div>
                      <div class="metric-small">
                        <p class="label">Time Saved</p>
                        <p class="value has-text-primary">45h</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="glass-card floating-card-1">
                  <b-icon icon="database-check" type="is-success" size="is-medium"></b-icon>
                  <span>Data Validated</span>
                </div>
                <div class="glass-card floating-card-2">
                  <b-icon icon="robot" type="is-primary" size="is-medium"></b-icon>
                  <span>AI Suggestions Ready</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Partners Section -->
    <section class="section py-5 has-background-white border-bottom">
      <div class="container">
        <p class="has-text-centered is-uppercase has-text-grey-light is-size-7 mb-5 has-text-weight-semibold letter-spacing-wide">
          Trusted by Industry Leaders
        </p>
        <div class="level is-mobile opacity-50">
          <div class="level-item"><b-icon icon="alpha-a-circle" size="is-large"></b-icon></div>
          <div class="level-item"><b-icon icon="alpha-b-circle" size="is-large"></b-icon></div>
          <div class="level-item"><b-icon icon="alpha-g-circle" size="is-large"></b-icon></div>
          <div class="level-item"><b-icon icon="alpha-m-circle" size="is-large"></b-icon></div>
          <div class="level-item"><b-icon icon="alpha-n-circle" size="is-large"></b-icon></div>
          <div class="level-item"><b-icon icon="alpha-s-circle" size="is-large"></b-icon></div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="section is-medium">
      <div class="container">
        <div class="has-text-centered mb-6">
          <h2 class="title is-2 has-text-weight-bold">Powerful Features for Data Teams</h2>
          <p class="subtitle is-5 has-text-grey">
            Everything you need to maintain a pristine data ecosystem.
          </p>
        </div>

        <div class="columns is-multiline">
          <div v-for="feature in features" :key="feature.title" class="column is-4">
            <div class="card feature-card h-100 no-shadow border-hover">
              <div class="card-content p-6">
                <div class="icon-box mb-5" :class="`has-background-${feature.type}-light`">
                  <b-icon :icon="feature.icon" :type="`is-${feature.type}`" size="is-medium"></b-icon>
                </div>
                <h3 class="title is-5 mb-3">{{ feature.title }}</h3>
                <p class="has-text-grey">{{ feature.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="section is-medium has-background-light-alt">
      <div class="container">
        <div class="has-text-centered mb-6">
          <h2 class="title is-2 has-text-weight-bold">Simple 4-Step Process</h2>
          <p class="subtitle is-5 has-text-grey">
            Go from raw mess to production-ready in record time.
          </p>
        </div>

        <b-steps
          v-model="activeStep"
          :animated="true"
          :rounded="true"
          :has-navigation="false"
          type="is-primary"
        >
          <b-step-item step="1" label="Connect" icon="database-import">
            <div class="columns is-vcentered py-6">
              <div class="column is-5">
                <h3 class="title is-3">Import from Anywhere</h3>
                <p class="is-size-5 has-text-grey mb-5">
                  Connect directly to your cloud databases (Snowflake, BigQuery), 
                  APIs, or simply drag and drop your CSV/Excel files.
                </p>
                <b-message type="is-info" size="is-small">
                  Supports 50+ native integrations and any custom REST API.
                </b-message>
              </div>
              <div class="column is-6 is-offset-1">
                <img src="https://placehold.co/600x400/667eea/white?text=Connect+Sources" alt="Connect" class="rounded-lg shadow-xl">
              </div>
            </div>
          </b-step-item>

          <b-step-item step="2" label="Analyze" icon="magnify">
            <div class="columns is-vcentered py-6">
              <div class="column is-5">
                <h3 class="title is-3">AI Issue Detection</h3>
                <p class="is-size-5 has-text-grey mb-5">
                  Our AI models automatically scan for schema drifts, duplicates, 
                  outliers, and missing values across your entire dataset.
                </p>
                <ul class="custom-list mb-5">
                  <li><b-icon icon="check-circle" type="is-success" size="is-small"></b-icon> Schema Validation</li>
                  <li><b-icon icon="check-circle" type="is-success" size="is-small"></b-icon> Outlier Detection</li>
                  <li><b-icon icon="check-circle" type="is-success" size="is-small"></b-icon> PII Masking Suggestions</li>
                </ul>
              </div>
              <div class="column is-6 is-offset-1">
                <img src="https://placehold.co/600x400/48bb78/white?text=AI+Analysis" alt="Analyze" class="rounded-lg shadow-xl">
              </div>
            </div>
          </b-step-item>

          <b-step-item step="3" label="Clean" icon="broom">
            <div class="columns is-vcentered py-6">
              <div class="column is-5">
                <h3 class="title is-3">Smart Transformations</h3>
                <p class="is-size-5 has-text-grey mb-5">
                  Apply complex cleaning rules with zero code. Standardize addresses, 
                  normalize names, and merge duplicates with high-confidence matching.
                </p>
                <div class="buttons">
                  <b-button type="is-primary" outlined rounded>Deduplicate</b-button>
                  <b-button type="is-info" outlined rounded>Standardize</b-button>
                  <b-button type="is-success" outlined rounded>Enrich</b-button>
                </div>
              </div>
              <div class="column is-6 is-offset-1">
                <img src="https://placehold.co/600x400/ed8936/white?text=Transformation+Engine" alt="Clean" class="rounded-lg shadow-xl">
              </div>
            </div>
          </b-step-item>

          <b-step-item step="4" label="Export" icon="database-export">
            <div class="columns is-vcentered py-6">
              <div class="column is-5">
                <h3 class="title is-3">Sync & Automate</h3>
                <p class="is-size-5 has-text-grey mb-5">
                  Sync your cleaned data back to your production database or 
                  automate the entire pipeline to run weekly.
                </p>
                <b-button type="is-primary" size="is-medium" rounded @click="goGetStarted">
                  Setup Your First Pipeline
                </b-button>
              </div>
              <div class="column is-6 is-offset-1">
                <img src="https://placehold.co/600x400/a0aec0/white?text=Export+Clean+Data" alt="Export" class="rounded-lg shadow-xl">
              </div>
            </div>
          </b-step-item>
        </b-steps>

        <div class="buttons is-centered mt-6">
          <b-button
            type="is-primary"
            outlined
            rounded
            icon-left="chevron-left"
            :disabled="activeStep === 0"
            @click="activeStep--"
          >
            Previous
          </b-button>
          <b-button
            type="is-primary"
            rounded
            icon-right="chevron-right"
            :disabled="activeStep === 3"
            @click="activeStep++"
          >
            Next Step
          </b-button>
        </div>
      </div>
    </section>

    <!-- Testimonials Section -->
    <section class="section is-medium">
      <div class="container">
        <div class="has-text-centered mb-6">
          <h2 class="title is-2">Loved by Data Engineers</h2>
        </div>
        
        <b-carousel
          :autoplay="true"
          :indicator="true"
          :indicator-inside="false"
          :indicator-background="false"
          :indicator-mode="'click'"
          :indicator-position="'is-bottom'"
          type="is-primary"
          class="testimonial-carousel"
        >
          <b-carousel-item v-for="(testimonial, i) in testimonials" :key="i">
            <div class="testimonial-content py-6 px-4 has-text-centered">
              <p class="is-size-3 is-italic mb-5 serif-font">"{{ testimonial.text }}"</p>
              <div class="testimonial-meta">
                <img :src="testimonial.avatar" class="avatar-large mb-3">
                <p class="has-text-weight-bold is-size-5">{{ testimonial.name }}</p>
                <p class="has-text-grey">{{ testimonial.role }} @ {{ testimonial.company }}</p>
              </div>
            </div>
          </b-carousel-item>
        </b-carousel>
      </div>
    </section>

    <!-- FAQ Section -->
    <section class="section is-medium has-background-white">
      <div class="container is-max-desktop">
        <div class="has-text-centered mb-6">
          <h2 class="title is-2">Frequently Asked Questions</h2>
        </div>
        
        <div class="faq-container">
          <b-collapse
            v-for="(faq, index) in faqs"
            :key="index"
            class="card mb-3 no-shadow border"
            animation="slide"
            :open="isOpen === index"
            @open="isOpen = index"
          >
            <template #trigger="props">
              <div class="card-header" role="button">
                <p class="card-header-title py-4 px-5">
                  {{ faq.question }}
                </p>
                <a class="card-header-icon">
                  <b-icon :icon="props.open ? 'minus' : 'plus'"></b-icon>
                </a>
              </div>
            </template>
            <div class="card-content px-5">
              <div class="content has-text-grey">
                {{ faq.answer }}
              </div>
            </div>
          </b-collapse>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="section is-large">
      <div class="container">
        <div class="cta-box has-background-primary p-6 rounded-2xl has-text-centered has-text-white relative overflow-hidden">
          <div class="cta-pattern"></div>
          <div class="relative z-10">
            <h2 class="title is-1 has-text-white mb-4">Start Cleaning Your Data Today</h2>
            <p class="subtitle is-4 has-text-white opacity-90 mb-6">
              Join 10,000+ professionals using MasterDataCleaner to win back their time.
            </p>
            <div class="buttons is-centered">
              <b-button
                type="is-white"
                size="is-large"
                rounded
                class="px-6 has-text-weight-bold has-text-primary"
                @click="goGetStarted"
              >
                Create Free Account
              </b-button>
              <b-button
                type="is-primary"
                inverted
                outlined
                size="is-large"
                rounded
                class="px-6"
                @click="contactSales"
              >
                Talk to Sales
              </b-button>
            </div>
            <p class="mt-5 is-size-7 opacity-75">
              <b-icon icon="check" size="is-small"></b-icon> No credit card required 
              <span class="mx-2">•</span> 
              <b-icon icon="check" size="is-small"></b-icon> 14-day free trial 
              <span class="mx-2">•</span> 
              <b-icon icon="check" size="is-small"></b-icon> Setup in 2 minutes
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeStep = ref(0)
const isOpen = ref(0)

const features = [
  {
    title: 'AI Deduplication',
    description: 'Fuzzy matching algorithms that find duplicate records across messy datasets with 99% accuracy.',
    icon: 'content-duplicate',
    type: 'primary'
  },
  {
    title: 'Address Standardization',
    description: 'Verify and format global addresses against official postal databases in real-time.',
    icon: 'map-marker-check',
    type: 'info'
  },
  {
    title: 'PII Protection',
    description: 'Automatically detect and mask sensitive information like emails, phone numbers, and IDs.',
    icon: 'shield-lock',
    type: 'success'
  },
  {
    title: 'Schema Mapping',
    description: 'Intelligent field mapping that learns your data structure and automates future imports.',
    icon: 'vector-arrange-below',
    type: 'warning'
  },
  {
    title: 'Data Enrichment',
    description: 'Enhance your data with external signals like company size, industry, and social profiles.',
    icon: 'plus-circle',
    type: 'link'
  },
  {
    title: 'API First',
    description: 'Everything you can do in the UI is available via our robust, high-performance API.',
    icon: 'api',
    type: 'danger'
  }
]

const testimonials = [
  {
    text: 'MasterDataCleaner saved our team over 200 hours of manual Excel work in just the first month.',
    name: 'Sarah Chen',
    role: 'Lead Data Engineer',
    company: 'TechFlow',
    avatar: 'https://i.pravatar.cc/150?u=sarah'
  },
  {
    text: 'The AI deduplication is magic. It found matches we would have never seen manually.',
    name: 'Marcus Thorne',
    role: 'VP of Operations',
    company: 'LogiGlobal',
    avatar: 'https://i.pravatar.cc/150?u=marcus'
  },
  {
    text: 'Security was our main concern, and their SOC 2 compliance and PII masking made it an easy choice.',
    name: 'Elena Rodriguez',
    role: 'CISO',
    company: 'FinSecure',
    avatar: 'https://i.pravatar.cc/150?u=elena'
  }
]

const faqs = [
  {
    question: 'How do you ensure data privacy?',
    answer: 'We are SOC 2 Type II compliant. Your data is encrypted at rest and in transit. We also offer on-premise deployment for enterprise customers with strict data residency requirements.'
  },
  {
    question: 'Which file formats do you support?',
    answer: 'We support CSV, Excel, JSON, XML, Parquet, and Avro. We also have native connectors for Snowflake, BigQuery, PostgreSQL, MongoDB, and Salesforce.'
  },
  {
    question: 'How accurate is the AI cleaning?',
    answer: 'Our models are trained on billions of real-world data points and consistently achieve over 99% accuracy in deduplication and normalization tasks.'
  },
  {
    question: 'Can I build custom cleaning rules?',
    answer: 'Yes! You can use our visual rule builder or write custom Python/JavaScript scripts for complex business logic.'
  }
]

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
  background-color: #fff;
}

/* Utils */
.mb-6 { margin-bottom: 3rem !important; }
.mt-6 { margin-top: 3rem !important; }
.py-6 { padding-top: 3rem !important; padding-bottom: 3rem !important; }
.rounded-lg { border-radius: 12px; }
.rounded-2xl { border-radius: 24px; }
.shadow-xl { box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); }
.overflow-hidden { overflow: hidden; }
.relative { position: relative; }
.z-10 { z-index: 10; }
.opacity-50 { opacity: 0.5; }
.opacity-75 { opacity: 0.75; }
.opacity-90 { opacity: 0.9; }
.h-100 { height: 100%; }

/* Typography */
.gradient-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.serif-font {
  font-family: 'Georgia', serif;
}

.letter-spacing-wide {
  letter-spacing: 0.1em;
}

/* Animations */
.animate-fade-in-left {
  animation: fadeInLeft 0.8s ease-out;
}

.animate-fade-in-right {
  animation: fadeInRight 0.8s ease-out;
}

@keyframes fadeInLeft {
  from { opacity: 0; transform: translateX(-30px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes fadeInRight {
  from { opacity: 0; transform: translateX(30px); }
  to { opacity: 1; transform: translateX(0); }
}

/* Hero Enhancements */
.hero {
  background-color: #f8faff;
}

.hero-background-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: radial-gradient(#667eea 0.5px, transparent 0.5px);
  background-size: 24px 24px;
  opacity: 0.05;
}

.glow-tag {
  box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.avatar-group {
  display: flex;
  align-items: center;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid white;
  margin-left: -8px;
}

.avatar:first-child { margin-left: 0; }

.avatar-more {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f0f0f0;
  border: 2px solid white;
  margin-left: -8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
  color: #666;
}

/* Hero Card Visual */
.hero-card-container {
  position: relative;
  padding: 2rem;
}

.glass-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
}

.main-preview {
  width: 100%;
  height: 320px;
}

.card-header-mock {
  padding: 12px;
  border-bottom: 1px solid rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
  gap: 12px;
}

.window-dots {
  display: flex;
  gap: 6px;
}

.window-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ddd;
}

.search-bar-mock {
  background: #f0f0f0;
  border-radius: 4px;
  font-size: 10px;
  padding: 4px 12px;
  color: #999;
  flex: 1;
}

.data-cleaning-animation {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: relative;
}

.data-row {
  display: flex;
  gap: 8px;
}

.cell-mock {
  background: #f5f5f5;
  height: 30px;
  border-radius: 4px;
  flex: 1;
  display: flex;
  align-items: center;
  padding: 0 8px;
  font-size: 11px;
}

.cell-mock.danger { background: #fee2e2; color: #ef4444; }
.cell-mock.success { background: #dcfce7; color: #22c55e; }

.cleaning-line {
  height: 2px;
  background: linear-gradient(to right, transparent, #667eea, transparent);
  width: 100%;
  animation: moveLine 2s infinite linear;
}

@keyframes moveLine {
  0% { opacity: 0; transform: scaleX(0); }
  50% { opacity: 1; transform: scaleX(1); }
  100% { opacity: 0; transform: scaleX(0); }
}

.metric-small {
  text-align: center;
  flex: 1;
}

.metric-small .label { font-size: 9px; color: #999; margin-bottom: 2px; }
.metric-small .value { font-size: 14px; font-weight: bold; }

.floating-card-1 {
  position: absolute;
  top: -10px;
  right: 0;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  font-weight: 500;
  animation: float 4s infinite ease-in-out;
}

.floating-card-2 {
  position: absolute;
  bottom: 0;
  left: 0;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  font-weight: 500;
  animation: float 4s infinite ease-in-out 1s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* Features */
.icon-box {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-card {
  transition: all 0.3s ease;
}

.no-shadow { box-shadow: none !important; }
.border { border: 1px solid #f0f0f0 !important; }
.border-hover:hover {
  border-color: #667eea;
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
}

/* Steps Enhancements */
.has-background-light-alt {
  background-color: #fcfdfe;
}

.custom-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.custom-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #4a4a4a;
}

/* Testimonials */
.avatar-large {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
}

.testimonial-carousel :deep(.carousel-indicator) {
  margin-top: 2rem;
}

/* CTA Box */
.cta-box {
  position: relative;
  box-shadow: 0 30px 60px -12px rgba(102, 126, 234, 0.4);
}

.cta-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 86c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zm66-3c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zm-46-45c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm26 18c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm16 18c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zM9 41c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm39 42c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm-24-6c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zM1 29c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm33-22c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm65 8c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zM28 49c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm66 31c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm-33-5c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm-20-47c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm4 32c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm-27-2c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zM86 52c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm-60 7c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm0-72c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zM16 52c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm44 40c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zM71 19c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zM4 72c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm67 4c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zM48 7c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zM25 1c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm23 23c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm-24 13c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm47 33c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm21-43c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm-19 -7c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zM17 10c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm80 49c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm-40 -22c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zM44 54c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1zm-27 10c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1z' fill='%23ffffff' fill-opacity='0.1' fill-rule='evenodd'/%3E%3C/svg%3E");
}

/* Responsive */
@media (max-width: 768px) {
  .hero-card-container {
    margin-top: 3rem;
    padding: 1rem;
  }
  
  .main-preview { height: 280px; }
  
  .floating-card-1, .floating-card-2 {
    display: none;
  }
}
</style>
