<template>
  <div class="integrations-page">
    <Breadcrumb :items="breadcrumbItems" />
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="mb-0">Integrations</h4>
      <BButton
        variant="primary"
        size="sm"
        @click="openCreateModal"
        :disabled="creating"
      >
        <template #left>
          <i class="bi bi-plus-lg me-1"></i>
        </template>
        New Search Engine
      </BButton>
    </div>

    <BAlert variant="info" show v-if="loading && engines.length === 0">
      Loading integrations…
    </BAlert>

    <BAlert variant="warning" show v-if="!loading && engines.length === 0">
      No search engines configured. Click "New Search Engine" to add one.
    </BAlert>

    <BTable
      v-else
      :items="engines"
      :fields="engineFields"
      :current-page="currentPage"
      :per-page="perPage"
      :sort-by="sortBy"
      @update:sortBy="onSortChange"
      sticky-header
      outline
    >
      <template #cell(provider)="data">
        <BBadge variant="light" pill class="border">
          {{ providerLabel(data.item.provider) }}
        </BBadge>
      </template>
      <template #cell(api_key_status)="data">
        <span v-if="data.item.has_api_key" class="text-success small">
          <i class="bi bi-key me-1"></i>Set
        </span>
        <span v-else class="text-muted small">—</span>
      </template>
      <template #cell(config)="data">
        <span v-if="data.item.config && Object.keys(data.item.config).length" class="small">
          <BBadge variant="outline-secondary" pill>{{ Object.keys(data.item.config).length }} params</BBadge>
        </span>
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
          @click="editEngineFn(data.item)"
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
        {{ Math.min(currentPage * perPage, engines.length) }}
        of
        {{ engines.length }}
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
          :disabled="currentPage === Math.ceil(engines.length / perPage) || engines.length === 0"
          @click="currentPage++"
        >
          Next ›
        </BButton>
      </BButtonGroup>
    </div>

    <!-- Create Search Engine Modal -->
    <BModal
      v-model="showCreateModal"
      title="Create Search Engine"
      @ok="createEngineFn"
      :ok-disabled="creating || !createFormValid"
      size="lg"
    >
      <BForm class="mt-3">
        <BFormGroup label="Name *:" label-for="create-name">
          <BFormInput
            id="create-name"
            v-model="createEngine.name"
            type="text"
            required
            placeholder="e.g., My DuckDuckGo Search"
          ></BFormInput>
        </BFormGroup>

        <BFormGroup label="Provider *:" label-for="create-provider">
          <BFormSelect
            id="create-provider"
            v-model="createEngine.provider"
            :options="providerOptions"
            required
          ></BFormSelect>
          <small v-if="selectedCreateProviderMeta" class="text-muted d-block mt-1">
            {{ selectedCreateProviderMeta.description }}
          </small>
        </BFormGroup>

        <BFormGroup
          v-if="selectedCreateProviderMeta?.requires_api_key"
          label="API Key *:"
          label-for="create-api-key"
          class="mt-2"
        >
          <BFormInput
            id="create-api-key"
            v-model="createEngine.api_key"
            type="password"
            placeholder="Your search provider API key"
          ></BFormInput>
        </BFormGroup>

        <!-- SearXNG-specific: searx_host field -->
        <BFormGroup
          v-if="createEngine.provider === 'searxng'"
          label="SearXNG Host URL *:"
          label-for="create-searx-host"
          class="mt-2"
        >
          <BFormInput
            id="create-searx-host"
            v-model="createEngineConfig.searx_host"
            type="url"
            placeholder="e.g., https://seek.fyi or http://localhost:8080"
          ></BFormInput>
          <small class="text-muted">URL of your SearXNG instance</small>
        </BFormGroup>

        <!-- Custom REST API fields -->
        <template v-if="createEngine.provider === 'custom'">
          <BFormGroup label="HTTP Method:" label-for="create-method" class="mt-2">
            <BFormSelect
              id="create-method"
              v-model="createEngineConfig.method"
              :options="[
                { value: 'GET', text: 'GET' },
                { value: 'POST', text: 'POST' },
              ]"
            ></BFormSelect>
          </BFormGroup>
          <BFormGroup label="URL *:" label-for="create-url" class="mt-2">
            <BFormInput
              id="create-url"
              v-model="createEngineConfig.url"
              type="url"
              placeholder="https://my-api.com/search"
            ></BFormInput>
          </BFormGroup>
          <BFormGroup label="Headers (JSON):" label-for="create-headers" class="mt-2">
            <BFormTextarea
              id="create-headers"
              v-model="createCustomHeaders"
              rows="2"
              placeholder='{"Authorization": "Bearer xxx"}'
            ></BFormTextarea>
          </BFormGroup>
          <BFormGroup label="Query Params (JSON):" label-for="create-params" class="mt-2">
            <BFormTextarea
              id="create-params"
              v-model="createCustomParams"
              rows="2"
              placeholder='{"key": "value"}'
            ></BFormTextarea>
          </BFormGroup>
          <BFormGroup label="Body Template (JSON, use {query} placeholder):" label-for="create-body" class="mt-2">
            <BFormTextarea
              id="create-body"
              v-model="createEngineConfig.body_template"
              rows="2"
              placeholder='{"query": "{query}"}'
            ></BFormTextarea>
          </BFormGroup>
        </template>

        <!-- Generic config JSON editor (for non-custom, non-searxng) -->
        <BFormGroup
          v-if="!['custom', 'searxng'].includes(createEngine.provider) && createEngine.provider"
          label="Additional Config (JSON, optional):"
          label-for="create-config"
          class="mt-2"
        >
          <BFormTextarea
            id="create-config"
            v-model="createConfigJson"
            rows="3"
            :placeholder="configExamplePlaceholder('create')"
          ></BFormTextarea>
          <small class="text-muted">JSON key-value pairs for provider-specific options</small>
        </BFormGroup>
      </BForm>

      <template #footer>
        <BButton @click="showCreateModal = false">Cancel</BButton>
        <BButton
          variant="primary"
          :disabled="creating || !createFormValid"
          @click="createEngineFn"
        >
          <template #left v-if="creating"><i class="bi bi-arrow-repeat me-1"></i></template>
          Create
        </BButton>
      </template>
    </BModal>

    <!-- Edit Search Engine Modal -->
    <BModal
      v-model="showEditModal"
      title="Edit Search Engine"
      @ok="updateEngineFn"
      :ok-disabled="updating || !editFormValid"
      size="lg"
    >
      <BForm class="mt-3">
        <BFormGroup label="Name *:" label-for="edit-name">
          <BFormInput
            id="edit-name"
            v-model="editEngine.name"
            type="text"
            required
          ></BFormInput>
        </BFormGroup>

        <BFormGroup label="Provider:" label-for="edit-provider">
          <BFormSelect
            id="edit-provider"
            v-model="editEngine.provider"
            :options="providerOptions"
            disabled
          ></BFormSelect>
          <small class="text-muted d-block mt-1">Provider cannot be changed after creation</small>
        </BFormGroup>

        <BFormGroup
          v-if="selectedEditProviderMeta?.requires_api_key"
          label="API Key:"
          label-for="edit-api-key"
          class="mt-2"
        >
          <BFormInput
            id="edit-api-key"
            v-model="editEngine.api_key"
            type="password"
            :placeholder="editEngine.has_api_key ? '•••••••• (leave blank to keep current)' : 'Your search provider API key'"
          ></BFormInput>
          <small v-if="editEngine.has_api_key && !editEngine.api_key" class="text-muted">
            API key is set. Enter a new value to replace it.
          </small>
        </BFormGroup>

        <!-- SearXNG-specific: searx_host field -->
        <BFormGroup
          v-if="editEngine.provider === 'searxng'"
          label="SearXNG Host URL *:"
          label-for="edit-searx-host"
          class="mt-2"
        >
          <BFormInput
            id="edit-searx-host"
            v-model="editEngineConfig.searx_host"
            type="url"
            placeholder="e.g., https://seek.fyi or http://localhost:8080"
          ></BFormInput>
        </BFormGroup>

        <!-- Custom REST API fields -->
        <template v-if="editEngine.provider === 'custom'">
          <BFormGroup label="HTTP Method:" label-for="edit-method" class="mt-2">
            <BFormSelect
              id="edit-method"
              v-model="editEngineConfig.method"
              :options="[
                { value: 'GET', text: 'GET' },
                { value: 'POST', text: 'POST' },
              ]"
            ></BFormSelect>
          </BFormGroup>
          <BFormGroup label="URL *:" label-for="edit-url" class="mt-2">
            <BFormInput
              id="edit-url"
              v-model="editEngineConfig.url"
              type="url"
              placeholder="https://my-api.com/search"
            ></BFormInput>
          </BFormGroup>
          <BFormGroup label="Headers (JSON):" label-for="edit-headers" class="mt-2">
            <BFormTextarea
              id="edit-headers"
              v-model="editCustomHeaders"
              rows="2"
              placeholder='{"Authorization": "Bearer xxx"}'
            ></BFormTextarea>
          </BFormGroup>
          <BFormGroup label="Query Params (JSON):" label-for="edit-params" class="mt-2">
            <BFormTextarea
              id="edit-params"
              v-model="editCustomParams"
              rows="2"
              placeholder='{"key": "value"}'
            ></BFormTextarea>
          </BFormGroup>
          <BFormGroup label="Body Template (JSON, use {query} placeholder):" label-for="edit-body" class="mt-2">
            <BFormTextarea
              id="edit-body"
              v-model="editEngineConfig.body_template"
              rows="2"
              placeholder='{"query": "{query}"}'
            ></BFormTextarea>
          </BFormGroup>
        </template>

        <!-- Generic config JSON editor (for non-custom, non-searxng) -->
        <BFormGroup
          v-if="!['custom', 'searxng'].includes(editEngine.provider) && editEngine.provider"
          label="Additional Config (JSON, optional):"
          label-for="edit-config"
          class="mt-2"
        >
          <BFormTextarea
            id="edit-config"
            v-model="editConfigJson"
            rows="3"
            :placeholder="configExamplePlaceholder('edit')"
          ></BFormTextarea>
          <small class="text-muted">JSON key-value pairs for provider-specific options</small>
        </BFormGroup>
      </BForm>

      <template #footer>
        <BButton @click="showEditModal = false">Cancel</BButton>
        <BButton
          variant="primary"
          :disabled="updating || !editFormValid"
          @click="updateEngineFn"
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
        <strong>Are you sure you want to delete this search engine?</strong><br />
        Any agents using this search engine will lose their search capability.
        This action cannot be undone.
      </div>
      <template #footer>
        <BButton @click="showDeleteConfirm = false">Cancel</BButton>
        <BButton
          variant="danger"
          :disabled="deleting"
          @click="deleteEngineFn"
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
  BAlert,
  BTable,
  BButtonGroup,
  BBadge,
} from 'bootstrap-vue-next';
import { useToast } from '@/composables/useToast';
import Breadcrumb from '@/components/Breadcrumb.vue';

const toast = useToast();

const API_URL = '/api';
const getAuthHeader = () => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`,
});

// --- State ---
const engines = ref([]);
const providers = ref([]);
const loading = ref(false);
const creating = ref(false);
const updating = ref(false);
const deleting = ref(false);
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showDeleteConfirm = ref(false);

const currentPage = ref(1);
const perPage = ref(10);
const sortBy = ref([{ key: 'created_at', order: 'desc' }]);

let selectedEngineId = null;

// --- Create form state ---
const createEngine = ref({
  name: '',
  provider: 'duckduckgo',
  api_key: '',
});
const createEngineConfig = ref({
  searx_host: '',
  method: 'GET',
  url: '',
  body_template: '',
});
const createConfigJson = ref('');
const createCustomHeaders = ref('');
const createCustomParams = ref('');

// --- Edit form state ---
const editEngine = ref({
  name: '',
  provider: '',
  api_key: '',
  has_api_key: false,
});
const editEngineConfig = ref({
  searx_host: '',
  method: 'GET',
  url: '',
  body_template: '',
});
const editConfigJson = ref('');
const editCustomHeaders = ref('');
const editCustomParams = ref('');

// --- Provider metadata ---
const selectedCreateProviderMeta = computed(() => {
  return providers.value.find(p => p.provider === createEngine.value.provider);
});

const selectedEditProviderMeta = computed(() => {
  return providers.value.find(p => p.provider === editEngine.value.provider);
});

const providerOptions = computed(() => {
  return [
    { value: '', text: 'Select a provider…', disabled: true },
    ...providers.value.map(p => ({
      value: p.provider,
      text: p.requires_api_key ? `${p.label} (API Key required)` : p.label,
    })),
  ];
});

function providerLabel(provider) {
  const meta = providers.value.find(p => p.provider === provider);
  return meta ? meta.label : provider;
}

function configExamplePlaceholder(mode) {
  const engine = mode === 'create' ? createEngine.value : editEngine.value;
  const meta = providers.value.find(p => p.provider === engine.provider);
  if (meta?.config_example) {
    return JSON.stringify(meta.config_example, null, 2);
  }
  return '{}';
}

// --- Table fields ---
const engineFields = computed(() => [
  { key: 'name', label: 'Name', sortable: true },
  { key: 'provider', label: 'Provider', sortable: true },
  { key: 'api_key_status', label: 'API Key', sortable: false },
  { key: 'config', label: 'Config', sortable: false },
  { key: 'created_at', label: 'Created', sortable: true },
  { key: 'actions', label: 'Actions', sortable: false },
]);

// --- Form validation ---
const createFormValid = computed(() => {
  if (!createEngine.value.name) return false;
  if (!createEngine.value.provider) return false;
  if (selectedCreateProviderMeta.value?.requires_api_key && !createEngine.value.api_key) return false;
  if (createEngine.value.provider === 'searxng' && !createEngineConfig.value.searx_host) return false;
  if (createEngine.value.provider === 'custom' && !createEngineConfig.value.url) return false;
  return true;
});

const editFormValid = computed(() => {
  if (!editEngine.value.name) return false;
  if (editEngine.value.provider === 'searxng' && !editEngineConfig.value.searx_host) return false;
  if (editEngine.value.provider === 'custom' && !editEngineConfig.value.url) return false;
  return true;
});

// --- Build config payload ---
function buildConfigPayload(provider, engineConfig, configJson, customHeaders, customParams) {
  if (provider === 'custom') {
    const config = {
      method: engineConfig.method || 'GET',
      url: engineConfig.url,
    };
    if (customHeaders) {
      try { config.headers = JSON.parse(customHeaders); } catch {}
    }
    if (customParams) {
      try { config.params = JSON.parse(customParams); } catch {}
    }
    if (engineConfig.body_template) {
      config.body_template = engineConfig.body_template;
    }
    return config;
  }

  if (provider === 'searxng') {
    const config = { searx_host: engineConfig.searx_host };
    if (configJson) {
      try {
        const extra = JSON.parse(configJson);
        Object.assign(config, extra);
      } catch {}
    }
    return config;
  }

  // Generic providers
  if (configJson) {
    try {
      return JSON.parse(configJson);
    } catch {}
  }
  return null;
}

// --- API calls ---
const fetchProviders = async () => {
  try {
    const res = await fetch(`${API_URL}/search-engines/providers`, {
      headers: getAuthHeader(),
    });
    if (res.ok) {
      providers.value = await res.json();
    }
  } catch {
    providers.value = [];
  }
};

const fetchEngines = async () => {
  loading.value = true;
  try {
    const res = await fetch(`${API_URL}/search-engines/`, {
      headers: getAuthHeader(),
    });
    if (!res.ok) {
      console.warn(`Failed to fetch search engines: ${res.status}`);
      engines.value = [];
    } else {
      const data = await res.json();
      engines.value = Array.isArray(data) ? data : [];
    }
  } catch (e) {
    console.error(e);
    toast.error('Failed to load search engines');
    engines.value = [];
  } finally {
    loading.value = false;
  }
};

const openCreateModal = () => {
  createEngine.value = { name: '', provider: 'duckduckgo', api_key: '' };
  createEngineConfig.value = { searx_host: '', method: 'GET', url: '', body_template: '' };
  createConfigJson.value = '';
  createCustomHeaders.value = '';
  createCustomParams.value = '';
  showCreateModal.value = true;
};

const createEngineFn = async () => {
  creating.value = true;
  try {
    const config = buildConfigPayload(
      createEngine.value.provider,
      createEngineConfig.value,
      createConfigJson,
      createCustomHeaders.value,
      createCustomParams.value,
    );

    const payload = {
      name: createEngine.value.name,
      provider: createEngine.value.provider,
      api_key: createEngine.value.api_key || null,
      config,
    };

    const res = await fetch(`${API_URL}/search-engines/`, {
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
    toast.success('Search engine created');
    showCreateModal.value = false;
    await fetchEngines();
  } catch (e) {
    console.error(e);
    toast.error(e.message || 'Could not create search engine');
  } finally {
    creating.value = false;
  }
};

const editEngineFn = (engine) => {
  editEngine.value = { ...engine };
  selectedEngineId = engine.id;

  // Parse existing config
  const config = engine.config || {};
  if (engine.provider === 'searxng') {
    editEngineConfig.value = {
      searx_host: config.searx_host || '',
      method: 'GET',
      url: '',
      body_template: '',
    };
    // Put remaining config keys into generic JSON
    const extra = { ...config };
    delete extra.searx_host;
    editConfigJson.value = Object.keys(extra).length ? JSON.stringify(extra, null, 2) : '';
  } else if (engine.provider === 'custom') {
    editEngineConfig.value = {
      searx_host: '',
      method: config.method || 'GET',
      url: config.url || '',
      body_template: config.body_template || '',
    };
    editCustomHeaders.value = config.headers ? JSON.stringify(config.headers, null, 2) : '';
    editCustomParams.value = config.params ? JSON.stringify(config.params, null, 2) : '';
    editConfigJson.value = '';
  } else {
    editEngineConfig.value = { searx_host: '', method: 'GET', url: '', body_template: '' };
    editConfigJson.value = config && Object.keys(config).length ? JSON.stringify(config, null, 2) : '';
  }

  showEditModal.value = true;
};

const updateEngineFn = async () => {
  updating.value = true;
  try {
    const config = buildConfigPayload(
      editEngine.value.provider,
      editEngineConfig.value,
      editConfigJson,
      editCustomHeaders.value,
      editCustomParams.value,
    );

    const payload = {
      name: editEngine.value.name,
      config,
    };

    // Only send api_key if user entered a new one
    if (editEngine.value.api_key) {
      payload.api_key = editEngine.value.api_key;
    }

    const res = await fetch(`${API_URL}/search-engines/${selectedEngineId}`, {
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
    toast.success('Search engine updated');
    showEditModal.value = false;
    await fetchEngines();
  } catch (e) {
    console.error(e);
    toast.error(e.message || 'Could not update search engine');
  } finally {
    updating.value = false;
  }
};

const confirmDelete = (engine) => {
  selectedEngineId = engine.id;
  showDeleteConfirm.value = true;
};

const deleteEngineFn = async () => {
  deleting.value = true;
  try {
    const res = await fetch(`${API_URL}/search-engines/${selectedEngineId}`, {
      method: 'DELETE',
      headers: getAuthHeader(),
    });
    if (!res.ok && res.status !== 204) {
      const err = await res.json();
      throw new Error(err.detail || 'Delete failed');
    }
    toast.success('Search engine deleted');
    showDeleteConfirm.value = false;
    await fetchEngines();
  } catch (e) {
    console.error(e);
    toast.error(e.message || 'Could not delete search engine');
  } finally {
    deleting.value = false;
  }
};

// --- Utilities ---
const onSortChange = (val) => {
  if (Array.isArray(val)) {
    sortBy.value = val;
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
  { label: 'Integrations', icon: 'bi bi-plug' },
];

// --- Lifecycle ---
onMounted(() => {
  fetchProviders();
  fetchEngines();
});

watch(
  () => engines.value,
  () => {
    const totalPages = Math.max(1, Math.ceil(engines.value.length / perPage.value));
    if (currentPage.value > totalPages) {
      currentPage.value = totalPages;
    }
  }
);
</script>

<style scoped>
.integrations-page {
  padding: 1rem;
}
</style>
