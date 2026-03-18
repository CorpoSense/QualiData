<template>
  <div class="agent-manager">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="mb-0">AI Agents</h4>
      <BButton
        variant="primary"
        size="sm"
        @click="showCreateModal = true"
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
      No agents yet. Click “New Agent” to create your first AI configuration.
    </BAlert>

    <BTable
      v-else
      :items="agents"
      :fields="agentFields"
      :current-page="currentPage"
      :per-page="perPage"
      :filter-included-fields="['name', 'provider', 'model', 'description']"
      :sort-by="sortBy"
      :sort-desc="sortDesc"
      @update:sort="onSortChange"
      sticky-header
      outline
    >
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
    >
      <BForm ref="createForm">
        <BFormGroup label="Agent Name *:" label-for="create-name">
          <BFormInput
            id="create-name"
            v-model="createAgent.name"
            type="text"
            required
            placeholder="e.g., My OpenAI Agent"
          ></BFormInput>
          <BFormInvalidFeedback
            v-if="!$refs.createForm.checkValidity() && !createAgent.name"
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
            placeholder="E.g., &quot;Extract {field} from the following text:&quot;"
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
    >
      <BForm ref="editForm">
        <BFormGroup label="Agent Name *:" label-for="edit-name">
          <BFormInput
            id="edit-name"
            v-model="editAgent.name"
            type="text"
            required
          ></BFormInput>
          <BFormInvalidFeedback
            v-if="!$refs.editForm.checkValidity() && !editAgent.name"
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
      :hide-footer="true"
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
import { ref, reactive, computed, onMounted, watch } from 'vue';
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
} from 'bootstrap-vue-next';
import { useToast } from '@/composables/useToast';

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

const currentPage = ref(1);
const perPage = ref(10);
const sortBy = ref('created_at');
const sortDesc = ref(true);

const createAgent = ref({
  name: '',
  description: '',
  provider: 'openai',
  model: '',
  system_prompt: '',
  prompt_template: '',
  temperature: 0.3,
});
const editAgent = ref({});
let selectedAgentId = null;

const agentFields = computed(() => [
  { key: 'name', label: 'Name', sortable: true },
  {
    key: 'provider_model',
    label: 'Provider / Model',
    sortable: false,
  },
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
];
];

const createFormValid = computed(() => {
  const form = $refs.createForm
  if (!form) return false
  return !!createAgent.value.name && createAgent.value.temperature >= 0 && createAgent.value.temperature <= 2
});

const editFormValid = computed(() => {
  const form = $refs.editForm
  if (!form) return false
  return !!editAgent.value.name && editAgent.value.temperature >= 0 && editAgent.value.temperature <= 2
});

const fetchAgents = async () => {
  loading.value = true;
  try {
    const res = await fetch(`${API_URL}/agents`, {
      headers: getAuthHeader(),
    });
    if (!res.ok) {
      // If the endpoint is not found or any other error, treat as empty list
      console.warn(`Failed to fetch agents: ${res.status}`)
      agents.value = []
    } else {
      const data = await res.json()
      agents.value = data
    }
  } catch (e) {
    console.error(e)
    toast.error('Failed to load agents')
    agents.value = []
  } finally {
    loading.value = false
  }
};

const createAgentFn = async () => {
  creating.value = true;
  try {
    const res = await fetch(`${API_URL}/agents`, {
      method: 'POST',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(createAgent.value),
    });
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Creation failed')
    }
    toast.success('Agent created')
    showCreateModal.value = false
    // reset form
    Object.assign(createAgent.value, {
      name: '',
      description: '',
      provider: 'openai',
      model: '',
      system_prompt: '',
      prompt_template: '',
      temperature: 0.3,
    })
    await fetchAgents()
  } catch (e) {
    console.error(e)
    toast.error(e.message || 'Could not create agent')
  } finally {
    creating.value = false
  }
};

const editAgentFn = (agent) => {
  // clone to avoid mutating the source until save
  editAgent.value = { ...agent }
  selectedAgentId = agent.id
  showEditModal.value = true
};

const updateAgentFn = async () => {
  updating.value = true;
  try {
    const res = await fetch(`${API_URL}/agents/${selectedAgentId}`, {
      method: 'PATCH',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(editAgent.value),
    });
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Update failed')
    }
    toast.success('Agent updated')
    showEditModal.value = false
    await fetchAgents()
  } catch (e) {
    console.error(e)
    toast.error(e.message || 'Could not update agent')
  } finally {
    updating.value = false
  }
};

const confirmDelete = (agent) => {
  selectedAgentId = agent.id
  showDeleteConfirm.value = true
};

const deleteAgentFn = async () => {
  deleting.value = true;
  try {
    const res = await fetch(`${API_URL}/agents/${selectedAgentId}`, {
      method: 'DELETE',
      headers: getAuthHeader(),
    });
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Delete failed')
    }
    toast.success('Agent deleted')
    showDeleteConfirm.value = false
    await fetchAgents()
  } catch (e) {
    console.error(e)
    toast.error(e.message || 'Could not delete agent')
  } finally {
    deleting.value = false
  }
};

onMounted(() => {
  fetchAgents();
});

watch(
  () => agents.value,
  () => {
    const totalPages = Math.max(1, Math.ceil(agents.value.length / perPage.value))
    if (currentPage.value > totalPages) {
      currentPage.value = totalPages
    }
  }
);

const onSortChange = (context) => {
  if (context.sortBy) {
    sortBy.value = context.sortBy
    sortDesc.value = context.sortDesc === true
  }
};
</script>

<style scoped>
.agent-manager {
  padding: 1rem;
}
</style>
