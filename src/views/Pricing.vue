<template>
  <div class="pricing-page">
    <div class="container">
      <!-- Header -->
      <div class="text-center mb-6">
        <h1 class="h1 mb-3">
          Simple, Transparent <span class="gradient-text">Pricing</span>
        </h1>
        <p class="h5 text-muted mb-4">
          Choose the plan that fits your needs. Upgrade or downgrade anytime.
        </p>
        
        <!-- Toggle -->
        <div class="toggle-container mt-5">
          <span :class="{ 'fw-bold': !isYearly }">Monthly</span>
          <BFormCheckbox v-model="isYearly" switch class="mx-3"></BFormCheckbox>
          <span :class="{ 'fw-bold': isYearly }">
            Yearly
            <BBadge variant="success" class="ms-2">Save 20%</BBadge>
          </span>
        </div>
      </div>

      <!-- Pricing Cards -->
      <div class="row justify-content-center">
        <div v-for="plan in plans" :key="plan.name" class="col-md-4 mb-4">
          <div class="card pricing-card" :class="{ 'featured': plan.featured }">
            <div v-if="plan.featured" class="popular-badge">
              <i class="bi bi-star-fill"></i>
              Most Popular
            </div>
            
            <div class="plan-header">
              <h3 class="h4 mb-2">{{ plan.name }}</h3>
              <p class="text-muted small">{{ plan.description }}</p>
            </div>
            
            <div class="plan-price mb-4">
              <span class="amount">${{ isYearly ? plan.yearlyPrice : plan.monthlyPrice }}</span>
              <span class="period">/month</span>
            </div>
            
            <ul class="features-list mb-5">
              <li v-for="feature in plan.features" :key="feature">
                <i class="bi bi-check-circle text-success me-2"></i>
                {{ feature }}
              </li>
              <li v-for="missing in plan.notIncluded" :key="missing" class="text-muted">
                <i class="bi bi-x-circle me-2"></i>
                {{ missing }}
              </li>
            </ul>
            
            <BButton 
              :variant="plan.featured ? 'primary' : 'outline-secondary'"
              size="md"
              block
              @click="selectPlan(plan)"
            >
              {{ plan.cta }}
            </BButton>
          </div>
        </div>
      </div>

      <!-- FAQ -->
      <div class="py-5">
        <div class="container" style="max-width: 800px;">
          <h2 class="h3 text-center mb-5">Frequently Asked Questions</h2>
          
          <BCollapse
            v-for="(faq, index) in faqs"
            :key="index"
            class="card mb-3"
            :visible="openFaq === index"
          >
            <template #trigger>
              <div class="card-header" role="button" @click="openFaq = openFaq === index ? -1 : index">
                <p class="card-title mb-0">{{ faq.question }}</p>
                <div class="card-header-icon">
                  <i :class="openFaq === index ? 'bi bi-dash' : 'bi bi-plus'"></i>
                </div>
              </div>
            </template>
            <div class="card-body">
              <p class="text-muted mb-0">{{ faq.answer }}</p>
            </div>
          </BCollapse>
        </div>
      </div>

      <!-- CTA -->
      <section class="py-5 bg-light">
        <div class="text-center">
          <h2 class="h3 mb-3">Need a Custom Plan?</h2>
          <p class="h5 text-muted mb-5">
            Contact us for custom pricing for enterprise needs.
          </p>
          <BButton variant="primary" size="lg" @click="contactSales">
            Contact Sales
          </BButton>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { BFormCheckbox, BBadge, BButton, BCollapse } from 'bootstrap-vue-next'

const isYearly = ref(false)
const openFaq = ref(0)

const plans = [
  {
    name: 'Free',
    description: 'Perfect for trying out the platform',
    monthlyPrice: 0,
    yearlyPrice: 0,
    features: [
      '1 Project',
      '100 rows per dataset',
      'Basic operations',
      'Community support',
      'CSV import/export'
    ],
    notIncluded: [
      'AI cleaning',
      'API access',
      'Priority support',
      'Team collaboration'
    ],
    cta: 'Get Started',
    featured: false
  },
  {
    name: 'Pro',
    description: 'For professionals and small teams',
    monthlyPrice: 29,
    yearlyPrice: 23,
    features: [
      '10 Projects',
      '10,000 rows per dataset',
      'All operations',
      'AI-powered cleaning',
      'Priority email support',
      'API access',
      'Team collaboration (up to 3)'
    ],
    notIncluded: [
      'Custom integrations',
      'Dedicated support'
    ],
    cta: 'Start Free Trial',
    featured: true
  },
  {
    name: 'Enterprise',
    description: 'For larger organizations',
    monthlyPrice: 99,
    yearlyPrice: 79,
    features: [
      'Unlimited Projects',
      'Unlimited rows',
      'All features',
      'Custom integrations',
      'Dedicated support',
      'SSO/SAML',
      'SLA guarantee',
      'On-premise option'
    ],
    notIncluded: [],
    cta: 'Contact Sales',
    featured: false
  }
]

const faqs = [
  {
    question: 'Can I cancel my subscription anytime?',
    answer: 'Yes, you can cancel your subscription at any time. Your access will continue until the end of your billing period.'
  },
  {
    question: 'What payment methods do you accept?',
    answer: 'We accept all major credit cards (Visa, MasterCard, American Express) and PayPal. Enterprise customers can also pay via invoice.'
  },
  {
    question: 'Is my data secure?',
    answer: 'Absolutely. We use industry-standard encryption (AES-256) for data at rest and TLS 1.3 for data in transit. We are SOC 2 Type II certified.'
  },
  {
    question: 'What happens if I exceed my row limit?',
    answer: 'You will be notified when you approach your limit. If you exceed it, your data is still safe - you just won\'t be able to add more rows until you upgrade or delete existing data.'
  },
  {
    question: 'Do you offer refunds?',
    answer: 'Yes, we offer a 14-day money-back guarantee for all paid plans. If you\'re not satisfied, contact us for a full refund.'
  }
]

const selectPlan = (plan) => {
  if (plan.monthlyPrice === 0) {
    console.log('Select free plan')
  } else if (plan.name === 'Enterprise') {
    contactSales()
  } else {
    console.log('Select plan:', plan.name)
  }
}

const contactSales = () => {
  window.location.href = 'mailto:sales@masterdatacleaner.com'
}
</script>

<style scoped>
.pricing-page {
  padding-top: 2rem;
  min-height: 100vh;
}

.gradient-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.toggle-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.pricing-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  position: relative;
  border: 1px solid #f0f0f0;
}

.pricing-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.pricing-card.featured {
  border-color: #667eea;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2);
}

.popular-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.plan-price {
  display: flex;
  align-items: baseline;
}

.plan-price .amount {
  font-size: 3rem;
  font-weight: 700;
  color: #333;
}

.plan-price .period {
  font-size: 1rem;
  color: #999;
  margin-left: 4px;
}

.features-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.features-list li {
  display: flex;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;
}

.card {
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #f8f9fa;
}

.card-title {
  font-weight: 500;
}
</style>
