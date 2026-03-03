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
      </div>

      <!-- Pricing Cards -->
      <PricingSection 
        title="" 
        subtitle="" 
        :show-toggle="true"
        @select-plan="selectPlan"
      />

      <!-- FAQ -->
      <div class="py-5">
        <div class="container" style="max-width: 800px;">
          <h2 class="h3 text-center mb-5">Frequently Asked Questions</h2>
          
          <div class="accordion" id="faqAccordion">
            <div class="accordion-item" v-for="(faq, index) in faqs" :key="index">
              <h2 class="accordion-header">
                <button 
                  class="accordion-button" 
                  :class="{ collapsed: openFaq !== index }" 
                  type="button" 
                  @click="openFaq = openFaq === index ? -1 : index"
                >
                  {{ faq.question }}
                </button>
              </h2>
              <div class="accordion-collapse collapse" :class="{ show: openFaq === index }">
                <div class="accordion-body text-muted">
                  {{ faq.answer }}
                </div>
              </div>
            </div>
          </div>
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
import { BButton } from 'bootstrap-vue-next'
import PricingSection from '@/components/PricingSection.vue'

const openFaq = ref(0)

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
</style>
