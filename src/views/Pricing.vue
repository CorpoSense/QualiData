<template>
  <div class="pricing-page">
    <div class="container">
      <!-- Header -->
      <div class="has-text-centered mb-6">
        <h1 class="title is-1 has-text-weight-bold">
          Simple, Transparent <span class="gradient-text">Pricing</span>
        </h1>
        <p class="subtitle is-4 has-text-grey">
          Choose the plan that fits your needs. Upgrade or downgrade anytime.
        </p>
        
        <!-- Toggle -->
        <div class="toggle-container mt-5">
          <span :class="{ 'has-text-weight-bold': !isYearly }">Monthly</span>
          <b-switch v-model="isYearly" class="mx-3" type="is-primary"></b-switch>
          <span :class="{ 'has-text-weight-bold': isYearly }">
            Yearly
            <b-tag type="is-success" size="is-small" class="ml-2">Save 20%</b-tag>
          </span>
        </div>
      </div>

      <!-- Pricing Cards -->
      <div class="columns is-centered">
        <div v-for="plan in plans" :key="plan.name" class="column is-4">
          <div class="pricing-card" :class="{ 'featured': plan.featured }">
            <div v-if="plan.featured" class="popular-badge">
              <b-icon icon="star" size="is-small"></b-icon>
              Most Popular
            </div>
            
            <div class="plan-header">
              <h3 class="title is-4 mb-2">{{ plan.name }}</h3>
              <p class="has-text-grey is-size-6">{{ plan.description }}</p>
            </div>
            
            <div class="plan-price mb-4">
              <span class="amount">${{ isYearly ? plan.yearlyPrice : plan.monthlyPrice }}</span>
              <span class="period">/month</span>
            </div>
            
            <ul class="features-list mb-5">
              <li v-for="feature in plan.features" :key="feature">
                <b-icon icon="check-circle" type="is-success" size="is-small" class="mr-2"></b-icon>
                {{ feature }}
              </li>
              <li v-for="missing in plan.notIncluded" :key="missing" class="has-text-grey-light">
                <b-icon icon="close-circle" size="is-small" class="mr-2"></b-icon>
                {{ missing }}
              </li>
            </ul>
            
            <b-button 
              :type="plan.featured ? 'is-primary' : 'is-light'"
              size="is-medium"
              expanded
              rounded
              @click="selectPlan(plan)"
            >
              {{ plan.cta }}
            </b-button>
          </div>
        </div>
      </div>

      <!-- FAQ -->
      <div class="section">
        <div class="container is-max-desktop">
          <h2 class="title is-3 has-text-centered mb-5">Frequently Asked Questions</h2>
          
          <b-collapse
            v-for="(faq, index) in faqs"
            :key="index"
            class="card mb-3"
            animation="slide"
            :open="openFaq === index"
            @open="openFaq = index"
          >
            <template #trigger>
              <div class="card-header" role="button">
                <p class="card-header-title">{{ faq.question }}</p>
                <a class="card-header-icon">
                  <b-icon :icon="openFaq === index ? 'minus' : 'plus'"></b-icon>
                </a>
              </div>
            </template>
            <div class="card-content">
              <p class="has-text-grey">{{ faq.answer }}</p>
            </div>
          </b-collapse>
        </div>
      </div>

      <!-- CTA -->
      <section class="section has-background-light">
        <div class="has-text-centered">
          <h2 class="title is-3">Need a Custom Plan?</h2>
          <p class="subtitle is-5 has-text-grey mb-5">
            Contact us for custom pricing for enterprise needs.
          </p>
          <b-button type="is-primary" size="is-large" rounded @click="contactSales">
            Contact Sales
          </b-button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

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
    // Navigate to signup
    console.log('Select free plan')
  } else if (plan.name === 'Enterprise') {
    contactSales()
  } else {
    // Navigate to checkout
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

.card-header-title {
  font-weight: 500;
}
</style>
