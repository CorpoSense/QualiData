<template>
  <div class="agent-manager">
    <Breadcrumb :items="breadcrumbItems" />
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="mb-0">AI Agents</h4>
      <BButton
        variant="primary"
        size="sm"
        @click="openCreateModal"
        :disabled="creating"
      >
        <template #left>
          <i class="bi bi-plus-lg me-1"></i>
        </template>
        New Agent
      </BButton>
    </div>

    <BAlert variant="info" show v-if="loading && agents.length === 0">
      Loading agents…
    </BAlert>

    <BAlert variant="warning" show v-if="!loading && agents.length === 0">
      No agents yet. Click "New Agent" to create your first AI configuration.
    </BAlert>

    <BTable
      v-else
      :items="agents"
      :fields="agentFields"
      :current-page="currentPage"
      :per-page="perPage"
      :sort-by="sortBy"
      @update:sortBy="onSortChange"
      sticky-header
      outline
    >
      <template #cell(provider_model)="data">
        <b>{{ data.item.provider }}</b>: {{ data.item.model }}
      </template>
      <template #cell(memory_type)="data">
        <BBadge v-if="data.item.memory_config" variant="info" pill class="small">
          {{ memoryTypeLabel(data.item.memory_config?.type) }}
        </BBadge>
        <span v-else class="text-muted small">—</span>
      </template>
      <template #cell(created_at)="data">
        {{ formatShortDate(data.item.created_at) }}
      </template>
      <template #cell(actions)="data">
        <BButton
          variant="outline-secondary"
          size="sm"
          class="me-1"
          @click="editAgentFn(data.item)"
          :disabled="updating"
        >
          <i class="bi bi-pencil"></i>
        </BButton>

        <BButton
          variant="outline-danger"
          size="sm"
          @click="confirmDelete(data.item)"
          :disabled="deleting"
        >
          <i class="bi bi-trash"></i>
        </BButton>
      </template>
    </BTable>

    <div class="d-flex justify-content-between align-items-center mt-2">
      <small class="text-muted">
        Showing
        {{ (currentPage - 1) * perPage + 1 }}–
        {{ Math.min(currentPage * perPage, agents.length) }}
        of
        {{ agents.length }}
      </small>

      <BButtonGroup size="sm">
        <BButton
          variant="outline-secondary"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          ‹ Prev
        </BButton>
        <BButton
          variant="outline-secondary"
          :disabled="currentPage === Math.ceil(agents.length / perPage) || agents.length === 0"
          @click="currentPage++"
        >
          Next ›
        </BButton>
      </BButtonGroup>
    </div>

    <!-- Create Agent Modal -->
    <BModal
      v-model="showCreateModal"
      title="Create New AI Agent"
      @ok="createAgentFn"
      :ok-disabled="creating || !createFormValid"
      size="lg"
    >
      <BTabs>
        <BTab title="Basic" active>
          <BForm ref="createForm" class="mt-3">
            <BFormGroup label="Agent Name *:" label-for="create-name">
              <BFormInput
                id="create-name"
                v-model="createAgent.name"
                type="text"
                required
                placeholder="e.g., My OpenAI Agent"
              ></BFormInput>
              <BFormInvalidFeedback
                v-if="( !createForm || !createForm.$el.checkValidity() ) && !createAgent.name"
              >
                Name is required.
              </BFormInvalidFeedback>
            </BFormGroup>

            <BFormGroup label="Description:" label-for="create-desc">
              <BFormTextarea
                id="create-desc"
                v-model="createAgent.description"
                rows="2"
                placeholder="Optional description of what this agent does"
              ></BFormTextarea>
            </BFormGroup>

            <BFormGroup label="Provider *:" label-for="create-provider">
              <BFormSelect
                id="create-provider"
                v-model="createAgent.provider"
                :options="providerOptions"
                required
              ></BFormSelect>
            </BFormGroup>

            <BFormGroup label="Model *:" label-for="create-model">
              <BFormInput
                id="create-model"
                v-model="createAgent.model"
                type="text"
                required
                placeholder="e.g., gpt-4o-mini"
                list="model-suggestions"
              ></BFormInput>
              <datalist id="model-suggestions">
                <option v-for="m in providerModels" :key="m" :value="m"></option>
              </datalist>
              <small v-if="!providerModels.length" class="text-muted">
                Enter API key above to load available models, or type a model name manually.
              </small>
            </BFormGroup>

            <BFormGroup label="API Key:" label-for="create-api-key">
              <BFormInput
                id="create-api-key"
                v-model="createAgent.api_key"
                type="password"
                placeholder="Your provider API key"
              ></BFormInput>
            </BFormGroup>

            <BFormGroup v-if="providersWithBaseUrl.includes(createAgent.provider)" label="Custom Base URL (optional):" label-for="create-base-url">
              <BFormInput
                id="create-base-url"
                v-model="createAgent.base_url"
                type="url"
                placeholder="e.g., http://localhost:11434 or https://your-proxy.com/v1"
              ></BFormInput>
            </BFormGroup>

            <BFormGroup label="System Prompt (optional):" label-for="create-system">
              <BFormTextarea
                id="create-system"
                v-model="createAgent.system_prompt"
                rows="2"
                placeholder="Optional system‑level instructions"
              ></BFormTextarea>
            </BFormGroup>

            <BFormGroup label="Prompt Template (optional):" label-for="create-template">
              <BFormTextarea
                id="create-template"
                v-model="createAgent.prompt_template"
                rows="2"
                placeholder='E.g., "Extract {field} from the following text:"'
              ></BFormTextarea>
            </BFormGroup>

            <BFormGroup label="Temperature (0‑2) *:" label-for="create-temp">
              <BFormInput
                id="create-temp"
                v-model="createAgent.temperature"
                type="number"
                min="0"
                max="2"
                step="0.1"
                required
              ></BFormInput>
              <BFormInvalidFeedback
                v-if="createAgent.temperature < 0 || createAgent.temperature > 2"
              >
                Must be between 0 and 2.
              </BFormInvalidFeedback>
            </BFormGroup>
          </BForm>
        </BTab>

        <BTab title="Advanced">
          <div class="mt-3">
            <BFormGroup label="Memory Strategy:" label-for="create-memory-type">
              <BFormSelect
                id="create-memory-type"
                v-model="createMemoryType"
                :options="memoryTypeOptions"
              ></BFormSelect>
              <small class="text-muted d-block mt-1">
                {{ memoryTypeDescription(createMemoryType) }}
              </small>
            </BFormGroup>

            <!-- Sliding Window params -->
            <BFormGroup
              v-if="createMemoryType === 'sliding_window'"
              label="Max Messages:"
              label-for="create-max-messages"
              class="mt-2"
            >
              <BFormInput
                id="create-max-messages"
                v-model.number="createMemoryParams.max_messages"
                type="range"
                min="5"
                max="100"
                step="5"
              ></BFormInput>
              <div class="d-flex justify-content-between small text-muted">
                <span>5</span>
                <span class="fw-bold text-body">{{ createMemoryParams.max_messages }}</span>
                <span>100</span>
              </div>
            </BFormGroup>

            <!-- Summarizer params -->
            <template v-if="createMemoryType === 'summarizer'">
              <BFormGroup label="Trigger Tokens:" label-for="create-trigger-tokens" class="mt-2">
                <BFormInput
                  id="create-trigger-tokens"
                  v-model.number="createMemoryParams.trigger_tokens"
                  type="number"
                  min="1000"
                  max="128000"
                  step="500"
                ></BFormInput>
                <small class="text-muted">Summarize when conversation exceeds this token count</small>
              </BFormGroup>
              <BFormGroup label="Keep Messages:" label-for="create-keep-messages" class="mt-2">
                <BFormInput
                  id="create-keep-messages"
                  v-model.number="createMemoryParams.keep_messages"
                  type="number"
                  min="5"
                  max="50"
                  step="5"
                ></BFormInput>
                <small class="text-muted">Number of recent messages to keep after summarization</small>
              </BFormGroup>
            </template>

            <!-- Trim Tokens params -->
            <BFormGroup
              v-if="createMemoryType === 'trim_tokens'"
              label="Keep Recent Messages:"
              label-for="create-keep-recent"
              class="mt-2"
            >
              <BFormInput
                id="create-keep-recent"
                v-model.number="createMemoryParams.keep_recent"
                type="number"
                min="2"
                max="20"
                step="1"
              ></BFormInput>
              <small class="text-muted">Keep only the system message + this many recent messages</small>
            </BFormGroup>
          </div>
        </BTab>
      </BTabs>

      <template #footer>
        <BButton @click="showCreateModal = false">Cancel</BButton>
        <BButton
          variant="primary"
          :disabled="creating || !createFormValid"
          @click="createAgentFn"
        >
          <template #left v-if="creating"><i class="bi bi-arrow-repeat me-1"></i></template>
          Create
        </BButton>
      </template>
    </BModal>

    <!-- Edit Agent Modal -->
    <BModal
      v-model="showEditModal"
      title="Edit Agent"
      @ok="updateAgentFn"
      :ok-disabled="updating || !editFormValid"
      size="lg"
    >
      <BTabs>
        <BTab title="Basic" active>
          <BForm ref="editForm" class="mt-3">
            <BFormGroup label="Agent Name *:" label-for="edit-name">
              <BFormInput
                id="edit-name"
                v-model="editAgent.name"
                type="text"
                required
              ></BFormInput>
              <BFormInvalidFeedback
                v-if="( !editForm || !editForm.$el.checkValidity() ) && !editAgent.name"
              >
                Name is required.
              </BFormInvalidFeedback>
            </BFormGroup>

            <BFormGroup label="Description:" label-for="edit-desc">
              <BFormTextarea
                id="edit-desc"
                v-model="editAgent.description"
                rows="2"
              ></BFormTextarea>
            </BFormGroup>

            <BFormGroup label="Provider *:" label-for="edit-provider">
              <BFormSelect
                id="edit-provider"
                v-model="editAgent.provider"
                :options="providerOptions"
                required
              ></BFormSelect>
            </BFormGroup>

            <BFormGroup label="Model *:" label-for="edit-model">
              <BFormInput
                id="edit-model"
                v-model="editAgent.model"
                type="text"
                required
                list="model-suggestions"
              ></BFormInput>
            </BFormGroup>

            <BFormGroup label="API Key:" label-for="edit-api-key">
              <BFormInput
                id="edit-api-key"
                v-model="editAgent.api_key"
                type="password"
                :placeholder="editAgent.has_api_key ? '•••••••• (leave blank to keep current)' : 'Your provider API key'"
              ></BFormInput>
              <small v-if="editAgent.has_api_key && !editAgent.api_key" class="text-muted">
                API key is set. Enter a new value to replace it.
              </small>
            </BFormGroup>

            <BFormGroup v-if="providersWithBaseUrl.includes(editAgent.provider)" label="Custom Base URL (optional):" label-for="edit-base-url">
              <BFormInput
                id="edit-base-url"
                v-model="editAgent.base_url"
                type="url"
                :placeholder="editAgent.base_url || 'e.g., http://localhost:11434'"
              ></BFormInput>
            </BFormGroup>

            <BFormGroup label="System Prompt (optional):" label-for="edit-system">
              <BFormTextarea
                id="edit-system"
                v-model="editAgent.system_prompt"
                rows="2"
              ></BFormTextarea>
            </BFormGroup>

            <BFormGroup label="Prompt Template (optional):" label-for="edit-template">
              <BFormTextarea
                id="edit-template"
                v-model="editAgent.prompt_template"
                rows="2"
              ></BFormTextarea>
            </BFormGroup>

            <BFormGroup label="Temperature (0‑2) *:" label-for="edit-temp">
              <BFormInput
                id="edit-temp"
                v-model="editAgent.temperature"
                type="number"
                min="0"
                max="2"
                step="0.1"
                required
              ></BFormInput>
              <BFormInvalidFeedback
                v-if="editAgent.temperature < 0 || editAgent.temperature > 2"
              >
                Must be between 0 and 2.
              </BFormInvalidFeedback>
            </BFormGroup>
          </BForm>
        </BTab>

        <BTab title="Advanced">
          <div class="mt-3">
            <BFormGroup label="Memory Strategy:" label-for="edit-memory-type">
              <BFormSelect
                id="edit-memory-type"
                v-model="editMemoryType"
                :options="memoryTypeOptions"
              ></BFormSelect>
              <small class="text-muted d-block mt-1">
                {{ memoryTypeDescription(editMemoryType) }}
              </small>
            </BFormGroup>

            <!-- Sliding Window params -->
            <BFormGroup
              v-if="editMemoryType === 'sliding_window'"
              label="Max Messages:"
              label-for="edit-max-messages"
              class="mt-2"
            >
              <BFormInput
                id="edit-max-messages"
                v-model.number="editMemoryParams.max_messages"
                type="range"
                min="5"
                max="100"
                step="5"
              ></BFormInput>
              <div class="d-flex justify-content-between small text-muted">
                <span>5</span>
                <span class="fw-bold text-body">{{ editMemoryParams.max_messages }}</span>
                <span>100</span>
              </div>
            </BFormGroup>

            <!-- Summarizer params -->
            <template v-if="editMemoryType === 'summarizer'">
              <BFormGroup label="Trigger Tokens:" label-for="edit-trigger-tokens" class="mt-2">
                <BFormInput
                  id="edit-trigger-tokens"
                  v-model.number="editMemoryParams.trigger_tokens"
                  type="number"
                  min="1000"
                  max="128000"
                  step="500"
                ></BFormInput>
                <small class="text-muted">Summarize when conversation exceeds this token count</small>
              </BFormGroup>
              <BFormGroup label="Keep Messages:" label-for="edit-keep-messages" class="mt-2">
                <BFormInput
                  id="edit-keep-messages"
                  v-model.number="editMemoryParams.keep_messages"
                  type="number"
                  min="5"
                  max="50"
                  step="5"
                ></BFormInput>
                <small class="text-muted">Number of recent messages to keep after summarization</small>
              </BFormGroup>
            </template>

            <!-- Trim Tokens params -->
            <BFormGroup
              v-if="editMemoryType === 'trim_tokens'"
              label="Keep Recent Messages:"
              label-for="edit-keep-recent"
              class="mt-2"
            >
              <BFormInput
                id="edit-keep-recent"
                v-model.number="editMemoryParams.keep_recent"
                type="number"
                min="2"
                max="20"
                step="1"
              ></BFormInput>
              <small class="text-muted">Keep only the system message + this many recent messages</small>
            </BFormGroup>
          </div>
        </BTab>
      </BTabs>

      <template #footer>
        <BButton @click="showEditModal = false">Cancel</BButton>
        <BButton
          variant="primary"
          :disabled="updating || !editFormValid"
          @click="updateAgentFn"
        >
          <template #left v-if="updating"><i class="bi bi-arrow-repeat me-1"></i></template>
          Update
        </BButton>
      </template>
    </BModal>

    <!-- Delete Confirmation Modal -->
    <BModal
      v-model="showDeleteConfirm"
      title="Confirm Delete"
    >
      <div class="alert alert-danger">
        <strong>Are you sure you want to delete this agent?</strong><br />
        This action cannot be undone.
      </div>
      <template #footer>
        <BButton @click="showDeleteConfirm = false">Cancel</BButton>
        <BButton
          variant="danger"
          :disabled="deleting"
          @click="deleteAgentFn"
        >
          <template #left v-if="deleting"><i class="bi bi-arrow-repeat me-1"></i></template>
          Delete
        </BButton>
      </template>
    </BModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import {
  BButton,
  BModal,
  BForm,
  BFormInput,
  BFormSelect,
  BFormTextarea,
  BFormGroup,
  BFormInvalidFeedback,
  BAlert,
  BTable,
  BButtonGroup,
  BTabs,
  BTab,
  BBadge,
} from 'bootstrap-vue-next';
import { useToast } from '@/composables/useToast';
import Breadcrumb from '@/components/Breadcrumb.vue';

const toast = useToast();

const API_URL = '/api';
const getAuthHeader = () => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`,
});

const agents = ref([]);
const loading = ref(false);
const creating = ref(false);
const updating = ref(false);
const deleting = ref(false);
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showDeleteConfirm = ref(false);
const providerModels = ref([]);

const openCreateModal = () => {
  showCreateModal.value = true;
  fetchModels(createAgent.value.provider, createAgent.value.api_key);
};

async function fetchModels(provider, apiKey) {
  try {
    const params = new URLSearchParams()
    if (apiKey) params.set('api_key', apiKey)
    const url = `${API_URL}/ai/models/${provider}${params.toString() ? '?' + params : ''}`
    const res = await fetch(url, { headers: getAuthHeader() })
    if (res.ok) {
      const data = await res.json()
      providerModels.value = data.models || []
    }
  } catch { providerModels.value = [] }
}

const currentPage = ref(1);
const perPage = ref(10);
const sortBy = ref([{ key: 'created_at', order: 'desc' }]);
const sortDesc = ref(true);

const createAgent = ref({
  name: '',
  description: '',
  provider: 'openai',
  model: '',
  api_key: '',
  base_url: '',
  system_prompt: '',
  prompt_template: '',
  temperature: 0.3,
});
const editAgent = ref({});
let selectedAgentId = null;

// --- Memory config state ---
const createMemoryType = ref('none');
const createMemoryParams = ref({
  max_messages: 20,
  trigger_tokens: 4000,
  keep_messages: 20,
  keep_recent: 4,
});

const editMemoryType = ref('none');
const editMemoryParams = ref({
  max_messages: 20,
  trigger_tokens: 4000,
  keep_messages: 20,
  keep_recent: 4,
});

const memoryTypeOptions = [
  { value: 'none', text: 'None (default)' },
  { value: 'sliding_window', text: 'Sliding Window' },
  { value: 'summarizer', text: 'Summarizer' },
  { value: 'trim_tokens', text: 'Trim Tokens' },
];

const memoryTypeDescriptions = {
  none: 'No memory management. The full conversation history is sent every time.',
  sliding_window: 'Removes the oldest messages when the conversation exceeds a message count threshold. Simple and predictable.',
  summarizer: 'Summarizes older messages into a condensed summary when the token count exceeds a threshold. Best for preserving context in long tasks.',
  trim_tokens: 'Keeps only the system message and the most recent N messages. Discards everything else. Good for small context models.',
};

function memoryTypeDescription(type) {
  return memoryTypeDescriptions[type] || '';
}

function memoryTypeLabel(type) {
  const opt = memoryTypeOptions.find(o => o.value === type);
  return opt ? opt.text : type;
}

function buildMemoryConfig(memoryType, memoryParams) {
  if (memoryType === 'none') return null;
  if (memoryType === 'sliding_window') {
    return { type: 'sliding_window', max_messages: memoryParams.max_messages };
  }
  if (memoryType === 'summarizer') {
    return { type: 'summarizer', trigger_tokens: memoryParams.trigger_tokens, keep_messages: memoryParams.keep_messages };
  }
  if (memoryType === 'trim_tokens') {
    return { type: 'trim_tokens', keep_recent: memoryParams.keep_recent };
  }
  return null;
}

function parseMemoryConfig(config) {
  if (!config || typeof config !== 'object') {
    return { type: 'none', params: { max_messages: 20, trigger_tokens: 4000, keep_messages: 20, keep_recent: 4 } };
  }
  const type = config.type || 'none';
  const params = {
    max_messages: config.max_messages || 20,
    trigger_tokens: config.trigger_tokens || 4000,
    keep_messages: config.keep_messages || 20,
    keep_recent: config.keep_recent || 4,
  };
  return { type, params };
}

// Template refs
const createForm = ref(null);
const editForm = ref(null);

// Reactive counters to force form validation re-computation
const createFormDirty = ref(0);
const editFormDirty = ref(0);

const agentFields = computed(() => [
  { key: 'name', label: 'Name', sortable: true },
  {
    key: 'provider_model',
    label: 'Provider: Model',
    sortable: false,
  },
  { key: 'memory_type', label: 'Memory', sortable: false },
  { key: 'description', label: 'Description', sortable: false },
  { key: 'created_at', label: 'Created', sortable: true },
  { key: 'actions', label: 'Actions', sortable: false },
]);

const providerOptions = [
  { value: 'openai', text: 'OpenAI' },
  { value: 'anthropic', text: 'Anthropic' },
  { value: 'google', text: 'Google' },
  { value: 'ollama', text: 'Ollama' },
  { value: 'groq', text: 'Groq' },
  { value: 'deepseek', text: 'DeepSeek' },
  { value: 'openrouter', text: 'OpenRouter' },
  { value: 'huggingface', text: 'Huggingface' },
];

const providersWithBaseUrl = ['openai', 'huggingface', 'ollama', 'groq', 'deepseek'];

const createFormValid = computed(() => {
  // Depend on dirty counter to force re-evaluation
  createFormDirty.value;

  // Check basic validity from our model first
  const hasName = !!createAgent.value.name;
  const tempValid = createAgent.value.temperature >= 0 && createAgent.value.temperature <= 2;

  // If form ref is not available yet, rely on basic model validation
  if (!createForm.value) {
    return hasName && tempValid;
  }

  // Form is available, check its validity along with our model constraints
  return createForm.value.$el.checkValidity() && hasName && tempValid;
});

const editFormValid = computed(() => {
  // Depend on dirty counter to force re-evaluation
  editFormDirty.value;

  // Check basic validity from our model first
  const hasName = !!editAgent.value.name;
  const tempValid = editAgent.value.temperature >= 0 && editAgent.value.temperature <= 2;

  // If form ref is not available yet, rely on basic model validation
  if (!editForm.value) {
    return hasName && tempValid;
  }

  // Form is available, check its validity along with our model constraints
  return editForm.value.$el.checkValidity() && hasName && tempValid;
});

const fetchAgents = async () => {
  loading.value = true;
  try {
    const res = await fetch(`${API_URL}/agents/`, {
      headers: getAuthHeader(),
    });
    if (!res.ok) {
      // If the endpoint is not found or any other error, treat as empty list
      console.warn(`Failed to fetch agents: ${res.status}`);
      agents.value = [];
    } else {
      const data = await res.json();
      // Ensure agents.value is always an array
      agents.value = Array.isArray(data) ? data : [];
    }
  } catch (e) {
    console.error(e);
    toast.error('Failed to load agents');
    agents.value = [];
  } finally {
    loading.value = false;
  }
};

const createAgentFn = async () => {
  creating.value = true;
  try {
    const payload = {
      ...createAgent.value,
      memory_config: buildMemoryConfig(createMemoryType.value, createMemoryParams.value),
    };
    const res = await fetch(`${API_URL}/agents/`, {
      method: 'POST',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Creation failed');
    }
    toast.success('Agent created');
    showCreateModal.value = false;
    // reset form
    Object.assign(createAgent.value, {
      name: '',
      description: '',
      provider: 'openai',
      model: '',
      api_key: '',
      base_url: '',
      system_prompt: '',
      prompt_template: '',
      temperature: 0.3,
    });
    createMemoryType.value = 'none';
    createMemoryParams.value = { max_messages: 20, trigger_tokens: 4000, keep_messages: 20, keep_recent: 4 };
    await fetchAgents();
  } catch (e) {
    console.error(e);
    toast.error(e.message || 'Could not create agent');
  } finally {
    creating.value = false;
  }
};

const editAgentFn = (agent) => {
  // clone to avoid mutating the source until save
  editAgent.value = { ...agent };
  // Parse existing memory config
  const { type, params } = parseMemoryConfig(agent.memory_config);
  editMemoryType.value = type;
  editMemoryParams.value = { ...params };
  selectedAgentId = agent.id;
  showEditModal.value = true;
  fetchModels(agent.provider);
};

const updateAgentFn = async () => {
  updating.value = true;
  try {
    const payload = {
      ...editAgent.value,
      memory_config: buildMemoryConfig(editMemoryType.value, editMemoryParams.value),
    };
    const res = await fetch(`${API_URL}/agents/${selectedAgentId}`, {
      method: 'PATCH',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Update failed');
    }
    toast.success('Agent updated');
    showEditModal.value = false;
    await fetchAgents();
  } catch (e) {
    console.error(e);
    toast.error(e.message || 'Could not update agent');
  } finally {
    updating.value = false;
  }
};

const confirmDelete = (agent) => {
  selectedAgentId = agent.id;
  showDeleteConfirm.value = true;
};

const deleteAgentFn = async () => {
  deleting.value = true;
  try {
    const res = await fetch(`${API_URL}/agents/${selectedAgentId}`, {
      method: 'DELETE',
      headers: getAuthHeader(),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Delete failed');
    }
    toast.success('Agent deleted');
    showDeleteConfirm.value = false;
    await fetchAgents();
  } catch (e) {
    console.error(e);
    toast.error(e.message || 'Could not delete agent');
  } finally {
    deleting.value = false;
  }
};

onMounted(() => {
  fetchAgents();
});

watch(() => createAgent.value.provider, (p) => { if (p) fetchModels(p, createAgent.value.api_key) })
watch(() => createAgent.value.api_key, (k) => { if (k && createAgent.value.provider) fetchModels(createAgent.value.provider, k) })
watch(() => editAgent.value.provider, (p) => { if (p) fetchModels(p) })

// Watch form fields to force validation re-computation
watch(
  () => [
    createAgent.value.name,
    createAgent.value.description,
    createAgent.value.provider,
    createAgent.value.model,
    createAgent.value.api_key,
    createAgent.value.base_url,
    createAgent.value.system_prompt,
    createAgent.value.prompt_template,
    createAgent.value.temperature,
    createMemoryType.value,
    createMemoryParams.value.max_messages,
    createMemoryParams.value.trigger_tokens,
    createMemoryParams.value.keep_messages,
    createMemoryParams.value.keep_recent,
  ],
  () => { createFormDirty.value++ }
)

watch(
  () => [
    editAgent.value.name,
    editAgent.value.description,
    editAgent.value.provider,
    editAgent.value.model,
    editAgent.value.api_key,
    editAgent.value.base_url,
    editAgent.value.system_prompt,
    editAgent.value.prompt_template,
    editAgent.value.temperature,
    editMemoryType.value,
    editMemoryParams.value.max_messages,
    editMemoryParams.value.trigger_tokens,
    editMemoryParams.value.keep_messages,
    editMemoryParams.value.keep_recent,
  ],
  () => { editFormDirty.value++ }
)

watch(
  () => agents.value,
  () => {
    const totalPages = Math.max(1, Math.ceil(agents.value.length / perPage.value));
    if (currentPage.value > totalPages) {
      currentPage.value = totalPages;
    }
  }
);

const onSortChange = (val) => {
  if (Array.isArray(val)) {
    sortBy.value = val;
    sortDesc.value = val.length > 0 && val[0].order === 'desc';
  }
};

const formatShortDate = (dateStr) => {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  const day = String(d.getDate()).padStart(2, '0');
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const year = d.getFullYear();
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  return `${day}/${month}/${year} ${hours}:${minutes}`;
};

const breadcrumbItems = [
  { label: 'Dashboard', path: '/dashboard', icon: 'bi bi-house' },
  { label: 'Agents', icon: 'bi bi-robot' }
];
</script>

<style scoped>
.agent-manager {
  padding: 1rem;
}
</style>
