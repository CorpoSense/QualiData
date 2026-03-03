<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="py-5 position-relative overflow-hidden" style="background: linear-gradient(135deg, #f8faff 0%, #fff 100%);">
      <div class="container py-5">
        <div class="row align-items-center">
          <div class="col-lg-6 animate-fade-in-left">
            <BBadge variant="primary" class="mb-4 px-3 py-2" style="font-size: 0.9rem; box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);">
              <i class="bi bi-stars me-1"></i> Version 3.0 is here
            </BBadge>
            <h1 class="display-4 fw-bold mb-4">
              Master Your Data with
              <span class="gradient-text">AI Precision</span>
            </h1>
            <p class="lead text-muted mb-4">
              The ultimate platform for cleaning, normalizing, and enriching your master data. 
              Say goodbye to manual spreadsheets and hello to automated intelligence.
            </p>
            
            <div class="d-flex gap-3 flex-wrap">
              <BButton variant="primary" size="lg" @click="goGetStarted">
                Get Started Free
              </BButton>
              <BButton variant="outline-secondary" size="lg" @click="watchDemo">
                <i class="bi bi-play-fill me-2"></i> Watch Demo
              </BButton>
            </div>

            <div class="mt-5 d-flex align-items-center">
              <div class="d-flex">
                <img src="https://i.pravatar.cc/150?u=1" alt="User" class="rounded-circle" style="width: 32px; height: 32px; margin-left: -8px; border: 2px solid white;">
                <img src="https://i.pravatar.cc/150?u=2" alt="User" class="rounded-circle" style="width: 32px; height: 32px; margin-left: -8px; border: 2px solid white;">
                <img src="https://i.pravatar.cc/150?u=3" alt="User" class="rounded-circle" style="width: 32px; height: 32px; margin-left: -8px; border: 2px solid white;">
                <div class="rounded-circle bg-light d-flex align-items-center justify-content-center" style="width: 32px; height: 32px; margin-left: -8px; border: 2px solid white; font-size: 10px; font-weight: bold;">+2k</div>
              </div>
              <p class="small text-muted mb-0 ms-3">
                Joined by <strong>2,000+</strong> data engineers this month.
              </p>
            </div>
          </div>
          
          <div class="col-lg-6 mt-5 mt-lg-0">
            <div class="position-relative">
              <div class="glass-card p-4" style="border-radius: 16px; background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(10px); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);">
                <div class="d-flex align-items-center gap-3 mb-3 pb-3" style="border-bottom: 1px solid rgba(0,0,0,0.05);">
                  <div class="d-flex gap-2">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: #ddd;"></span>
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: #ddd;"></span>
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: #ddd;"></span>
                  </div>
                  <div class="bg-light rounded px-3 py-1 flex-grow-1" style="font-size: 10px; color: #999;">master-data-cleanup.csv</div>
                </div>
                <div class="mb-3">
                  <div class="d-flex gap-2 mb-2">
                    <div class="bg-light rounded px-3 py-2 flex-fill" style="font-size: 11px;">Jhn Doe</div>
                    <div class="bg-light rounded px-3 py-2 flex-fill" style="font-size: 11px;">ny, usa</div>
                    <div class="bg-danger bg-opacity-25 rounded px-3 py-2 flex-fill text-danger" style="font-size: 11px;">invalid_email</div>
                  </div>
                  <div class="border-bottom border-primary opacity-50 mb-2"></div>
                  <div class="d-flex gap-2">
                    <div class="bg-light rounded px-3 py-2 flex-fill" style="font-size: 11px;">John Doe</div>
                    <div class="bg-light rounded px-3 py-2 flex-fill" style="font-size: 11px;">New York, USA</div>
                    <div class="bg-success bg-opacity-25 rounded px-3 py-2 flex-fill text-success" style="font-size: 11px;">john@example.com</div>
                  </div>
                </div>
                <div class="d-flex justify-content-between">
                  <div class="text-center">
                    <p class="small text-muted mb-0">Accuracy</p>
                    <p class="fw-bold text-success mb-0">99.9%</p>
                  </div>
                  <div class="text-center">
                    <p class="small text-muted mb-0">Duplicates</p>
                    <p class="fw-bold text-danger mb-0">0</p>
                  </div>
                  <div class="text-center">
                    <p class="small text-muted mb-0">Time Saved</p>
                    <p class="fw-bold text-primary mb-0">45h</p>
                  </div>
                </div>
              </div>
              <div class="position-absolute bg-white rounded-3 p-3 d-flex align-items-center gap-2 shadow" style="top: -10px; right: 0; animation: float 4s infinite ease-in-out;">
                <i class="bi bi-check-circle text-success"></i>
                <span style="font-size: 13px;">Data Validated</span>
              </div>
              <div class="position-absolute bg-white rounded-3 p-3 d-flex align-items-center gap-2 shadow" style="bottom: 0; left: 0; animation: float 4s infinite ease-in-out 1s;">
                <i class="bi bi-robot text-primary"></i>
                <span style="font-size: 13px;">AI Suggestions Ready</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Partners Section -->
    <section class="py-4 border-bottom">
      <div class="container">
        <p class="text-center text-muted small text-uppercase mb-4" style="letter-spacing: 0.1em;">Trusted by Industry Leaders</p>
        <div class="d-flex justify-content-center gap-5 flex-wrap opacity-50">
          <i class="bi bi-alphabet" style="font-size: 2rem;"></i>
          <i class="bi bi-box-seam" style="font-size: 2rem;"></i>
          <i class="bi bi-cpu" style="font-size: 2rem;"></i>
          <i class="bi bi-globe" style="font-size: 2rem;"></i>
          <i class="bi bi-lightning" style="font-size: 2rem;"></i>
          <i class="bi bi-shield-check" style="font-size: 2rem;"></i>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-5">
      <div class="container py-5">
        <div class="text-center mb-5">
          <h2 class="h1 fw-bold mb-3">Powerful Features for Data Teams</h2>
          <p class="text-muted">Everything you need to maintain a pristine data ecosystem.</p>
        </div>

        <div class="row g-4">
          <div v-for="feature in features" :key="feature.title" class="col-md-4">
            <div class="card h-100 border-0 shadow-sm feature-card" style="transition: all 0.3s ease;">
              <div class="card-body p-4">
                <div class="icon-box mb-3" :class="`bg-${feature.type}-subtle`" style="width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                  <i :class="`bi bi-${feature.icon} text-${feature.type}`"></i>
                </div>
                <h3 class="h5 mb-3">{{ feature.title }}</h3>
                <p class="text-muted mb-0">{{ feature.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="py-5" style="background: #fcfdfe;">
      <div class="container py-5">
        <div class="text-center mb-5">
          <h2 class="h1 fw-bold mb-3">Simple 4-Step Process</h2>
          <p class="text-muted">Go from raw mess to production-ready in record time.</p>
        </div>

        <!-- Steps -->
        <div class="nav nav-pills mb-4 justify-content-center" role="tablist">
          <button v-for="(step, idx) in steps" :key="idx" class="nav-link" :class="{ active: activeStep === idx }" @click="activeStep = idx">
            <i :class="`bi bi-${step.icon} me-2`"></i>{{ step.label }}
          </button>
        </div>

        <div class="row align-items-center py-4">
          <div class="col-lg-5">
            <h3 class="h2">{{ steps[activeStep].title }}</h3>
            <p class="text-muted mb-4">{{ steps[activeStep].description }}</p>
            <ul class="list-unstyled">
              <li v-for="item in steps[activeStep].items" :key="item" class="d-flex align-items-center mb-2">
                <i class="bi bi-check-circle text-success me-2"></i> {{ item }}
              </li>
            </ul>
          </div>
          <div class="col-lg-6 offset-lg-1 mt-4 mt-lg-0">
            <div class="bg-light rounded-4 p-4 text-center">
              <i :class="`bi bi-${steps[activeStep].icon}`" style="font-size: 4rem; color: #667eea;"></i>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonials -->
    <section class="py-5">
      <div class="container py-5">
        <div class="text-center mb-5">
          <h2 class="h1 fw-bold mb-3">Loved by Data Teams</h2>
          <p class="text-muted">See what our customers have to say.</p>
        </div>

        <div class="row g-4">
          <div v-for="t in testimonials" :key="t.name" class="col-md-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body p-4">
                <p class="mb-4">"{{ t.text }}"</p>
                <div class="d-flex align-items-center">
                  <img :src="t.avatar" alt="" class="rounded-circle me-3" style="width: 48px; height: 48px;">
                  <div>
                    <p class="fw-bold mb-0">{{ t.name }}</p>
                    <p class="small text-muted mb-0">{{ t.role }}, {{ t.company }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Pricing Preview -->
    <PricingSection @select-plan="handlePlanSelect">
      <template #cta="{ plan }">
        <BButton 
          :variant="plan.featured ? 'primary' : 'outline-dark'" 
          block
          @click="plan.name === 'Enterprise' ? contactSales() : goGetStarted()"
        >
          {{ plan.cta }}
        </BButton>
      </template>
    </PricingSection>

    <!-- FAQ -->
    <section class="py-5">
      <div class="container py-5" style="max-width: 800px;">
        <h2 class="h1 fw-bold text-center mb-5">Frequently Asked Questions</h2>
        
        <div class="accordion" id="faqAccordion">
          <div class="accordion-item" v-for="(faq, idx) in faqs" :key="idx">
            <h2 class="accordion-header">
              <button class="accordion-button" :class="{ collapsed: isOpen !== idx }" type="button" @click="isOpen = isOpen === idx ? -1 : idx">
                {{ faq.question }}
              </button>
            </h2>
            <div class="accordion-collapse collapse" :class="{ show: isOpen === idx }">
              <div class="accordion-body text-muted">
                {{ faq.answer }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="py-5" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
      <div class="container py-5 text-center text-white">
        <h2 class="h1 fw-bold mb-3">Ready to Get Started?</h2>
        <p class="mb-4 opacity-75">Join thousands of teams already using MasterDataCleaner.</p>
        <div class="d-flex justify-content-center gap-3">
          <BButton size="lg" variant="light" @click="goGetStarted">Start Free</BButton>
          <BButton size="lg" variant="outline-light" @click="contactSales">Contact Sales</BButton>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-dark text-white py-5 mt-5">
      <div class="container py-4">
        <div class="row g-4">
          <div class="col-lg-4">
            <h5 class="fw-bold mb-3">MasterDataCleaner</h5>
            <p class="small text-white-50 mb-3">The ultimate platform for cleaning, normalizing, and enriching your master data with AI precision.</p>
            <div class="d-flex gap-3">
              <a href="#" class="text-white"><i class="bi bi-twitter-x"></i></a>
              <a href="#" class="text-white"><i class="bi bi-github"></i></a>
              <a href="#" class="text-white"><i class="bi bi-linkedin"></i></a>
            </div>
          </div>
          <div class="col-lg-2">
            <h6 class="fw-bold mb-3">Product</h6>
            <ul class="list-unstyled mb-0">
              <li class="mb-2"><a href="#" class="text-white-50 text-decoration-none">Features</a></li>
              <li class="mb-2"><a href="#" class="text-white-50 text-decoration-none">Pricing</a></li>
              <li class="mb-2"><a href="#" class="text-white-50 text-decoration-none">Integrations</a></li>
              <li class="mb-2"><a href="#" class="text-white-50 text-decoration-none">API</a></li>
            </ul>
          </div>
          <div class="col-lg-2">
            <h6 class="fw-bold mb-3">Company</h6>
            <ul class="list-unstyled mb-0">
              <li class="mb-2"><a href="#" class="text-white-50 text-decoration-none">About</a></li>
              <li class="mb-2"><a href="#" class="text-white-50 text-decoration-none">Blog</a></li>
              <li class="mb-2"><a href="#" class="text-white-50 text-decoration-none">Careers</a></li>
              <li class="mb-2"><a href="#" class="text-white-50 text-decoration-none">Contact</a></li>
            </ul>
          </div>
          <div class="col-lg-2">
            <h6 class="fw-bold mb-3">Legal</h6>
            <ul class="list-unstyled mb-0">
              <li class="mb-2"><a href="#" class="text-white-50 text-decoration-none">Privacy</a></li>
              <li class="mb-2"><a href="#" class="text-white-50 text-decoration-none">Terms</a></li>
              <li class="mb-2"><a href="#" class="text-white-50 text-decoration-none">Security</a></li>
            </ul>
          </div>
          <div class="col-lg-2">
            <h6 class="fw-bold mb-3">Support</h6>
            <ul class="list-unstyled mb-0">
              <li class="mb-2"><a href="#" class="text-white-50 text-decoration-none">Help Center</a></li>
              <li class="mb-2"><a href="#" class="text-white-50 text-decoration-none">Documentation</a></li>
              <li class="mb-2"><a href="#" class="text-white-50 text-decoration-none">Status</a></li>
            </ul>
          </div>
        </div>
        <hr class="my-4 border-secondary">
        <div class="d-flex justify-content-between align-items-center">
          <p class="small text-white-50 mb-0">&copy; 2026 MasterDataCleaner. All rights reserved.</p>
          <p class="small text-white-50 mb-0">Made with <i class="bi bi-heart-fill text-danger"></i> for data teams</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { BButton, BBadge } from 'bootstrap-vue-next'
import PricingSection from '@/components/PricingSection.vue'

const router = useRouter()
const activeStep = ref(0)
const isOpen = ref(0)

const features = [
  { title: 'AI Deduplication', description: 'Fuzzy matching algorithms that find duplicate records across messy datasets with 99% accuracy.', icon: 'copy', type: 'primary' },
  { title: 'Address Standardization', description: 'Verify and format global addresses against official postal databases in real-time.', icon: 'geo-alt', type: 'info' },
  { title: 'PII Protection', description: 'Automatically detect and mask sensitive information like emails, phone numbers, and IDs.', icon: 'shield-lock', type: 'success' },
  { title: 'Schema Mapping', description: 'Intelligent field mapping that learns your data structure and automates future imports.', icon: 'layout-text-window-reverse', type: 'warning' },
  { title: 'Data Enrichment', description: 'Enhance your data with external signals like company size, industry, and social profiles.', icon: 'plus-circle', type: 'secondary' },
  { title: 'API First', description: 'Everything you can do in the UI is available via our robust, high-performance API.', icon: 'plug', type: 'danger' }
]

const steps = [
  { label: 'Connect', icon: 'database-up', title: 'Import from Anywhere', description: 'Connect directly to your cloud databases or drag and drop files.', items: ['50+ native integrations', 'CSV, Excel, JSON support', 'Custom REST API'] },
  { label: 'Analyze', icon: 'search', title: 'AI Issue Detection', description: 'Let AI identify duplicates, missing values, and inconsistencies.', items: ['Auto-detect issues', 'Data quality score', 'Smart suggestions'] },
  { label: 'Clean', icon: 'magic', title: 'Automated Cleaning', description: 'Apply AI-powered transformations with a single click.', items: ['One-click deduplication', 'Auto-standardization', 'PII masking'] },
  { label: 'Export', icon: 'download', title: 'Export Anywhere', description: 'Send cleaned data to your production systems.', items: ['Multiple formats', 'Scheduled exports', 'API integration'] }
]

const testimonials = [
  { text: 'MasterDataCleaner saved our team over 200 hours of manual Excel work in just the first month.', name: 'Sarah Chen', role: 'Lead Data Engineer', company: 'TechFlow', avatar: 'https://i.pravatar.cc/150?u=sarah' },
  { text: 'The AI deduplication is magic. It found matches we would have never seen manually.', name: 'Marcus Thorne', role: 'VP of Operations', company: 'LogiGlobal', avatar: 'https://i.pravatar.cc/150?u=marcus' },
  { text: 'Security was our main concern, and their SOC 2 compliance and PII masking made it an easy choice.', name: 'Elena Rodriguez', role: 'CISO', company: 'FinSecure', avatar: 'https://i.pravatar.cc/150?u=elena' }
]

const faqs = [
  { question: 'How do you ensure data privacy?', answer: 'We are SOC 2 Type II compliant. Your data is encrypted at rest and in transit. We also offer on-premise deployment for enterprise customers.' },
  { question: 'Which file formats do you support?', answer: 'We support CSV, Excel, JSON, XML, Parquet, and Avro. We also have native connectors for Snowflake, BigQuery, PostgreSQL, MongoDB, and Salesforce.' },
  { question: 'How accurate is the AI cleaning?', answer: 'Our models are trained on billions of real-world data points and consistently achieve over 99% accuracy in deduplication and normalization tasks.' },
  { question: 'Can I build custom cleaning rules?', answer: 'Yes! You can use our visual rule builder or write custom Python/JavaScript scripts for complex business logic.' }
]

const goGetStarted = () => {
  router.push('/login')
}

const handlePlanSelect = (plan) => {
  if (plan.name === 'Enterprise') {
    contactSales()
  } else {
    goGetStarted()
  }
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

.gradient-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.animate-fade-in-left {
  animation: fadeInLeft 0.8s ease-out;
}

@keyframes fadeInLeft {
  from { opacity: 0; transform: translateX(-30px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
}

.bg-primary-subtle { background-color: rgba(102, 126, 234, 0.1); }
.bg-info-subtle { background-color: rgba(59, 130, 246, 0.1); }
.bg-success-subtle { background-color: rgba(34, 197, 94, 0.1); }
.bg-warning-subtle { background-color: rgba(234, 179, 8, 0.1); }
.bg-secondary-subtle { background-color: rgba(108, 117, 125, 0.1); }
.bg-danger-subtle { background-color: rgba(239, 68, 68, 0.1); }
</style>
