<template>
  <section class="py-5 bg-light">
    <div class="container py-5">
      <div class="text-center mb-5">
        <h2 class="h1 fw-bold mb-3">{{ title }}</h2>
        <p class="text-muted">{{ subtitle }}</p>
        
        <!-- Toggle -->
        <div v-if="showToggle" class="d-flex align-items-center justify-content-center mt-4">
          <span :class="{ 'fw-bold': !isYearly }">Monthly</span>
          <div class="form-check form-switch mx-3">
            <input class="form-check-input" type="checkbox" v-model="isYearly" id="pricingToggle">
          </div>
          <span :class="{ 'fw-bold': isYearly }">
            Yearly
            <span class="badge bg-success ms-2">Save 20%</span>
          </span>
        </div>
      </div>

      <div class="row justify-content-center g-4">
        <div v-for="plan in plans" :key="plan.name" class="col-md-4">
          <div 
            class="card border-0 shadow-sm h-100"
            :class="{ 'shadow-lg border-2': plan.featured }"
            :style="plan.featured ? 'border-color: #667eea !important;' : ''"
          >
            <div v-if="plan.featured" class="position-absolute top-0 start-50 translate-middle" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 4px 16px; border-radius: 20px; font-size: 12px; white-space: nowrap;">
              Most Popular
            </div>
            <div class="card-body p-4 text-center" :class="{ 'mt-3': plan.featured }">
              <h3>{{ plan.name }}</h3>
              <p class="display-4 fw-bold">
                ${{ isYearly ? plan.yearlyPrice : plan.monthlyPrice }}
                <small class="text-muted fs-6" v-if="plan.monthlyPrice > 0">/mo</small>
              </p>
              <p class="text-muted">{{ plan.description }}</p>
              
              <ul class="list-unstyled text-start mb-4">
                <li v-for="feature in plan.features" :key="feature" class="mb-2">
                  <i class="bi bi-check text-success me-2"></i>{{ feature }}
                </li>
                <li v-for="missing in plan.notIncluded" :key="missing" class="mb-2 text-muted">
                  <i class="bi bi-x me-2"></i>{{ missing }}
                </li>
              </ul>
              
              <slot name="cta" :plan="plan">
                <BButton 
                  :variant="plan.featured ? 'primary' : 'outline-dark'" 
                  block
                  @click="$emit('select-plan', plan)"
                >
                  {{ plan.cta }}
                </BButton>
              </slot>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { BButton } from 'bootstrap-vue-next'

const props = defineProps({
  title: { type: String, default: 'Simple Pricing' },
  subtitle: { type: String, default: 'Start free, scale as you grow.' },
  showToggle: { type: Boolean, default: false }
})

defineEmits(['select-plan'])

const isYearly = ref(false)

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

defineExpose({ plans, isYearly })
</script>
