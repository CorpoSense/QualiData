<template>
  <BModal v-model="show" title="Extract Pattern" size="lg" @hidden="onHidden">
    <div class="alert alert-info py-2 mb-3">
      <i class="bi bi-info-circle me-1"></i>
      Extract matching text from strings in <strong>{{ column }}</strong> using a regex pattern.
      Non-matching values are left unchanged.
    </div>

    <!-- Sample values -->
    <div v-if="samples.length" class="mb-3">
      <label class="form-label fw-bold small">Sample values:</label>
      <div class="bg-light p-2 rounded" style="max-height: 120px; overflow-y: auto;">
        <code v-for="(s, i) in samples" :key="i" class="d-block small text-truncate mb-1">{{ s }}</code>
      </div>
    </div>

    <!-- Common pattern presets -->
    <div class="mb-3">
      <label class="form-label fw-bold small">Common patterns:</label>
      <div class="d-flex flex-wrap gap-1">
        <button
          v-for="preset in presets"
          :key="preset.label"
          class="btn btn-sm"
          :class="pattern === preset.pattern ? 'btn-primary' : 'btn-outline-secondary'"
          @click="selectPreset(preset)"
          :title="preset.description"
        >{{ preset.label }}</button>
      </div>
    </div>

    <!-- Pattern input -->
    <BFormGroup label="Regex pattern" label-for="pattern-input" class="mb-3">
      <div class="d-flex gap-2">
        <BFormInput
          id="pattern-input"
          v-model="pattern"
          placeholder="e.g., https?://([^/]+)"
          :state="patternError ? false : null"
        />
        <BButton
          size="sm"
          variant="outline-info"
          @click="suggestPatternWithAI"
          :disabled="aiLoading || !pattern"
          title="Use AI to help write a regex pattern"
        >
          <i class="bi bi-stars me-1"></i>AI
        </BButton>
      </div>
      <div v-if="patternError" class="text-danger small mt-1">
        <i class="bi bi-exclamation-triangle me-1"></i>{{ patternError }}
      </div>
      <small class="text-muted">
        💡 Use capture groups <code>()</code> to extract only part of the match.
        E.g., <code>https?://([^/]+)</code> extracts just the domain.
      </small>
    </BFormGroup>

    <!-- Case sensitivity -->
    <div class="form-check mb-3">
      <input class="form-check-input" type="checkbox" v-model="caseSensitive" id="ep-case-sensitive">
      <label class="form-check-label" for="ep-case-sensitive">Case sensitive</label>
    </div>

    <!-- Live preview -->
    <div v-if="pattern && preview.length" class="mb-3">
      <label class="form-label fw-bold small">Preview (first {{ preview.length }} rows):</label>
      <div class="bg-light p-2 rounded" style="max-height: 200px; overflow-y: auto;">
        <div v-for="(p, i) in preview" :key="i" class="d-flex align-items-start gap-2 mb-1 small">
          <span v-if="p.changed" class="text-success"><i class="bi bi-check-circle"></i></span>
          <span v-else class="text-muted"><i class="bi bi-dash-circle"></i></span>
          <div>
            <code class="text-muted">{{ truncate(String(p.before), 60) }}</code>
            <span v-if="p.changed"> → <code class="text-success">{{ truncate(String(p.after), 60) }}</code></span>
            <span v-else class="text-muted"> (no change)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Suggestion Modal -->
    <BModal v-model="showAiModal" title="AI Regex Suggestion" size="md" no-close-on-backdrop>
      <div class="alert alert-info py-2 mb-3">
        <i class="bi bi-stars me-1"></i>
        Describe what you want to extract, and the AI will suggest a regex pattern.
      </div>
      <BFormGroup label="Describe what to extract" label-for="ai-prompt-input">
        <BFormInput
          id="ai-prompt-input"
          v-model="aiPrompt"
          placeholder="e.g., Extract the domain name from URLs"
        />
      </BFormGroup>
      <div v-if="samples.length" class="mt-2">
        <small class="text-muted">Sample values will be included as context:</small>
        <div class="bg-light p-1 rounded mt-1">
          <code v-for="(s, i) in samples.slice(0, 3)" :key="i" class="d-block small text-truncate">{{ s }}</code>
        </div>
      </div>
      <div v-if="aiError" class="alert alert-danger py-2 mt-2 small">{{ aiError }}</div>
      <div v-if="aiSuggestion" class="mt-2">
        <label class="form-label fw-bold small">Suggested pattern:</label>
        <div class="d-flex gap-2 align-items-center">
          <code class="bg-light p-2 rounded flex-grow-1">{{ aiSuggestion }}</code>
          <BButton size="sm" variant="primary" @click="applyAiSuggestion">Use this</BButton>
        </div>
        <small v-if="aiReasoning" class="text-muted d-block mt-1">{{ aiReasoning }}</small>
      </div>
      <template #footer>
        <BButton @click="showAiModal = false">Cancel</BButton>
        <BButton variant="primary" :disabled="!aiPrompt || aiLoading" :loading="aiLoading" @click="callAiSuggest">
          <i class="bi bi-stars me-1"></i>Suggest
        </BButton>
      </template>
    </BModal>

    <template #footer>
      <BButton @click="show = false">Cancel</BButton>
      <BButton variant="primary" :disabled="!pattern || !!patternError" :loading="loading" @click="apply">
        <i class="bi bi-regex me-1"></i>Extract
      </BButton>
    </template>
  </BModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { BModal, BFormGroup, BFormInput, BButton } from 'bootstrap-vue-next'
import { getApiUrl } from '@/utils/api'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  column: { type: String, default: '' },
  samples: { type: Array, default: () => [] },
  datasetId: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  agentOptions: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue', 'apply'])

const show = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const apiUrl = getApiUrl()
const toast = useToast()

const pattern = ref('')
const caseSensitive = ref(true)
const patternError = ref('')
const preview = ref([])

// AI suggestion state
const showAiModal = ref(false)
const aiPrompt = ref('')
const aiSuggestion = ref('')
const aiReasoning = ref('')
const aiLoading = ref(false)
const aiError = ref('')

const presets = [
  { label: 'URL domain', pattern: 'https?://([^/]+)', description: 'Extract domain from URLs' },
  { label: 'Email', pattern: '([\\w.+-]+@[\\w-]+\\.[\\w.]+)', description: 'Extract email addresses' },
  { label: 'Number', pattern: '(\\d+(?:\\.\\d+)?)', description: 'Extract first number' },
  { label: 'Date', pattern: '(\\d{4}-\\d{2}-\\d{2})', description: 'Extract YYYY-MM-DD dates' },
  { label: 'Phone', pattern: '(\\+?\\d[\\d\\s-]{7,}\\d)', description: 'Extract phone numbers' },
  { label: 'Word', pattern: '(\\w+)', description: 'Extract first word' },
]

function selectPreset(preset) {
  pattern.value = preset.pattern
}

// Validate pattern and generate preview
watch([pattern, caseSensitive], () => {
  patternError.value = ''
  preview.value = []

  if (!pattern.value) return

  try {
    const flags = caseSensitive.value ? '' : 'i'
    const regex = new RegExp(pattern.value, flags)
    // Generate preview from samples
    preview.value = props.samples.map(s => {
      const str = String(s ?? '').trim()
      if (!str) return { before: s, after: s, changed: false }
      const match = regex.exec(str)
      if (!match) return { before: s, after: s, changed: false }
      const result = (match.lastIndex !== undefined && match.length > 1 && match[1] !== undefined) ? match[1] : match[0]
      return { before: s, after: result, changed: String(result) !== String(s) }
    })
  } catch (e) {
    patternError.value = `Invalid regex: ${e.message}`
  }
}, { immediate: true })

function truncate(str, max) {
  return str.length > max ? str.slice(0, max) + '…' : str
}

function apply() {
  if (!pattern.value || patternError.value) return
  emit('apply', {
    pattern: pattern.value,
    case_sensitive: caseSensitive.value,
  })
}

function onHidden() {
  pattern.value = ''
  caseSensitive.value = true
  patternError.value = ''
  preview.value = []
  aiSuggestion.value = ''
  aiReasoning.value = ''
  aiPrompt.value = ''
  aiError.value = ''
}

function suggestPatternWithAI() {
  aiPrompt.value = ''
  aiSuggestion.value = ''
  aiReasoning.value = ''
  aiError.value = ''
  showAiModal.value = true
}

async function callAiSuggest() {
  if (!aiPrompt.value) return
  aiLoading.value = true
  aiError.value = ''
  aiSuggestion.value = ''
  aiReasoning.value = ''

  try {
    const token = localStorage.getItem('token')
    // Use the first available agent, or fallback to a simple chat endpoint
    const agentId = props.agentOptions.length > 1 ? props.agentOptions[1]?.value : null

    const systemPrompt = `You are a regex expert. Given a description of what to extract from text and sample values, suggest a Python-compatible regex pattern.
Rules:
- Respond with JSON only: {"pattern": "regex_here", "reasoning": "explanation"}
- Use capture groups () for the part to extract
- The pattern should work with Python's re.search()
- Be precise and test against the sample values`

    const userPrompt = `I want to extract: ${aiPrompt.value}

Sample values from the column "${props.column}":
${props.samples.slice(0, 5).map(s => `- "${s}"`).join('\n')}

Current pattern (if any): ${pattern.value || 'none'}

Suggest a regex pattern that extracts the desired value from these strings.`

    // Try using the AI chat endpoint
    const res = await fetch(`${apiUrl}/api/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        provider: agentId ? undefined : 'openai',
        model: undefined,
        message: userPrompt,
      }),
    })

    if (!res.ok) {
      // Fallback: try the suggest-fix endpoint
      const res2 = await fetch(`${apiUrl}/api/ai/suggest-fix`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          provider: 'openai',
          issue_description: userPrompt,
        }),
      })
      if (!res2.ok) {
        aiError.value = 'AI service unavailable. Please write the regex manually.'
        aiLoading.value = false
        return
      }
      const data2 = await res2.json()
      // Try to extract pattern from the suggestion text
      const patternMatch = data2.suggestion?.match(/["']([^"']+)["']/)
      if (patternMatch) {
        aiSuggestion.value = patternMatch[1]
        aiReasoning.value = data2.suggestion
      } else {
        aiError.value = 'Could not parse AI suggestion. Please write the regex manually.'
      }
      aiLoading.value = false
      return
    }

    const data = await res.json()
    const text = data.response || ''

    // Try to parse JSON from the response
    try {
      // Strip markdown fences if present
      let raw = text.trim()
      if (raw.startsWith('```')) {
        raw = raw.split('\n', 1)[1] || raw.slice(3)
      }
      if (raw.endsWith('```')) {
        raw = raw.slice(0, -3)
      }
      raw = raw.trim()
      const parsed = JSON.parse(raw)
      if (parsed.pattern) {
        aiSuggestion.value = parsed.pattern
        aiReasoning.value = parsed.reasoning || ''
      } else {
        aiError.value = 'AI did not return a pattern. Try a different description.'
      }
    } catch {
      // Try to extract a regex pattern from the text
      const patternMatch = text.match(/(?:pattern|regex)[:\s]+["`]([^"`]+)["`]/i)
      if (patternMatch) {
        aiSuggestion.value = patternMatch[1]
        aiReasoning.value = text
      } else {
        aiError.value = 'Could not parse AI response. Please write the regex manually.'
      }
    }
  } catch (e) {
    aiError.value = `AI error: ${e.message}`
  } finally {
    aiLoading.value = false
  }
}

function applyAiSuggestion() {
  if (aiSuggestion.value) {
    pattern.value = aiSuggestion.value
    showAiModal.value = false
    toast.success('AI pattern applied')
  }
}
</script>
