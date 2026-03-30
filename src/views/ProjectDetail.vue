<template>
  <div class="project-detail">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-5">
      <div>
        <BButton variant="link" @click="$router.push('/projects')" class="mb-3 ps-0">
          <i class="bi bi-arrow-left me-2"></i>Back to Projects
        </BButton>
        <h1 class="h3 mb-1">{{ project?.name }}</h1>
        <p class="text-muted">{{ project?.description || 'No description' }}</p>
      </div>
      <div class="d-flex gap-2">
        <BButton variant="primary" @click="showImportModal = true">
          <i class="bi bi-upload me-2"></i>Import Data
        </BButton>
        <BButton variant="success" @click="$router.push(`/assistant?project=${projectId}`)">
          <i class="bi bi-robot me-2"></i>AI Assistant
        </BButton>
      </div>
    </div>

    <!-- Stats -->
    <div class="row mb-5">
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <p class="text-muted small text-uppercase">Datasets</p>
            <p class="h3 mb-0">{{ datasets.length }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <p class="text-muted small text-uppercase">Total Rows</p>
            <p class="h3 mb-0">{{ formatNumber(project?.row_count || 0) }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <p class="text-muted small text-uppercase">Storage</p>
            <p class="h3 mb-0">{{ formatBytes(project?.storage_bytes || 0) }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <p class="text-muted small text-uppercase">Last Updated</p>
            <p class="h5 mb-0">{{ formatDate(project?.updated_at) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <BTabs v-model="activeTab" nav-style="box">
      <BTab title="Datasets">
        <!-- Datasets List -->
        <div v-if="loading" class="text-center py-6">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else-if="datasets.length === 0" class="card text-center py-6">
          <div class="card-body">
            <i class="bi bi-database text-muted mb-4" style="font-size: 3rem;"></i>
            <p class="text-muted mb-4">No datasets yet</p>
            <BButton variant="primary" @click="showImportModal = true">
              Import Your First Dataset
            </BButton>
          </div>
        </div>
        <div v-else>
          <!-- Dataset selection bar -->
          <div v-if="selectedDatasetIds.length > 0" class="d-flex align-items-center gap-2 mb-3 p-2 bg-light rounded">
            <span class="small text-muted">{{ selectedDatasetIds.length }} dataset(s) selected</span>
            <BButton size="sm" variant="outline-secondary" @click="selectedDatasetIds = []">Clear</BButton>
            <BButton v-if="selectedDatasetIds.length >= 2" size="sm" variant="primary" @click="openMergeModal">
              <i class="bi bi-arrows-collapse me-1"></i>Merge
            </BButton>
            <BButton size="sm" variant="danger" @click="confirmBulkDelete">
              <i class="bi bi-trash me-1"></i>Delete
            </BButton>
          </div>
          <div class="row">
          <div v-for="dataset in datasets" :key="dataset.id" class="col-md-4 mb-3">
            <div class="position-relative">
              <div class="position-absolute top-0 start-0 m-2" style="z-index: 1;">
                <input
                  class="form-check-input"
                  type="checkbox"
                  :checked="selectedDatasetIds.includes(dataset.id)"
                  @click.stop="toggleDatasetSelection(dataset.id)"
                  @change.stop
                >
              </div>
              <DatasetCard 
                :dataset="dataset"
                @click="viewDataset(dataset)"
              >
                <template #actions>
                  <BDropdownItem @click="previewDataset(dataset)">Preview</BDropdownItem>
                  <BDropdownItem @click="openRenameModal(dataset)">Rename</BDropdownItem>
                  <BDropdownItem @click="exportDataset(dataset)">Export</BDropdownItem>
                  <BDropdownItem @click="profileDataset(dataset)" variant="info">Profile</BDropdownItem>
                  <BDropdownItem @click="deleteDataset(dataset)" variant="danger">Delete</BDropdownItem>
                </template>
              </DatasetCard>
            </div>
          </div>
          </div>
        </div>
        <!-- Datasets pagination -->
        <div v-if="datasetTotal > datasetPageSize" class="d-flex justify-content-center mt-3">
          <BPagination
            v-model="datasetPage"
            :total-rows="datasetTotal"
            :per-page="datasetPageSize"
            @update:model-value="fetchDatasets"
          ></BPagination>
        </div>
      </BTab>

      <BTab title="Operations">
        <div class="card">
          <div class="card-body p-0">
            <div v-if="operations.length === 0" class="text-center py-5 text-muted">
              <i class="bi bi-clock-history" style="font-size: 3rem;"></i>
              <p class="mt-3 mb-0">No operations yet</p>
              <p class="small">Operations will appear here after you clean or transform data</p>
            </div>
            <div v-else class="operations-list">
              <div 
                v-for="op in operations" 
                :key="op.id"
                class="operation-item"
              >
                <div class="d-flex align-items-center gap-3">
                  <div class="operation-icon" :class="getOperationClass(op.operation_type)">
                    <i :class="getOperationIcon(op.operation_type)"></i>
                  </div>
                  <div class="flex-grow-1">
                    <div class="d-flex align-items-center gap-2 mb-1">
                      <strong>{{ formatOperationType(op.operation_type) }}</strong>
                      <span v-if="op.dataset_name" class="badge bg-light text-dark">{{ op.dataset_name }}</span>
                    </div>
                    <p class="small text-muted mb-0">{{ formatDate(op.created_at) }}</p>
                  </div>
                  <BBadge v-if="op.is_undone" variant="secondary">Undone</BBadge>
                  <BBadge v-else variant="success">Done</BBadge>
                  <button class="btn btn-sm btn-outline-secondary border-0 py-0 px-1" @click="showOpDetails(op)" title="View details">
                    <i class="bi bi-info-circle"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </BTab>
    </BTabs>

    <!-- Import Modal -->
    <BModal
      v-model="showImportModal"
      :has-modal-card="true"
      title="Import Data"
      size="lg"
    >
      <div class="p-3">
        <!-- Tabs -->
        <ul class="nav nav-pills mb-3">
          <li class="nav-item">
            <button class="nav-link" :class="{ active: importTab === 'file' }" @click="importTab = 'file'">
              <i class="bi bi-file-earmark-arrow-up me-1"></i> File
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link" :class="{ active: importTab === 'database' }" @click="importTab = 'database'">
              <i class="bi bi-database me-1"></i> Database
            </button>
          </li>
        </ul>

        <!-- File Import -->
        <div v-if="importTab === 'file'">
          <BFormGroup label="Dataset Name">
            <BFormInput v-model="importForm.name" placeholder="My Dataset"></BFormInput>
            <small class="text-muted">If empty, the first file name will be used. When merging multiple files, this name will be used for the merged dataset.</small>
          </BFormGroup>
          
          <!-- Multi-file Drop Zone -->
          <BFormGroup label="Upload Files" class="mt-3">
            <div
              class="drop-zone p-4 border rounded text-center"
              :class="{ 'drop-zone-active': isDragging }"
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="handleDrop"
              @click="triggerFileInput"
            >
              <input
                ref="fileInput"
                type="file"
                multiple
                accept=".csv,.tsv,.txt,.xlsx,.xls,.parquet"
                class="d-none"
                @change="handleFileSelect"
              >
              <i class="bi bi-cloud-arrow-up text-muted" style="font-size: 2rem;"></i>
              <p class="mb-1 mt-2">Drag & drop files here or click to browse</p>
              <small class="text-muted">CSV, TSV, Excel (.xlsx, .xls), Parquet (.parquet)</small>
            </div>
          </BFormGroup>

          <!-- File List -->
          <div v-if="importForm.files.length > 0" class="mt-3">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="small text-muted">{{ importForm.files.length }} file(s) selected</span>
              <BButton size="sm" variant="link" @click="clearFiles">Clear all</BButton>
            </div>
            <div class="file-list">
              <div
                v-for="(file, index) in importForm.files"
                :key="index"
                class="file-item d-flex align-items-center gap-2 p-2 border rounded mb-2"
              >
                <i class="bi bi-file-earmark-text text-muted"></i>
                <div class="flex-grow-1">
                  <div class="small">{{ file.name }}</div>
                  <div class="text-muted" style="font-size: 0.75rem;">{{ formatFileSize(file.size) }}</div>
                </div>
                <BButton size="sm" variant="link" class="text-danger p-0" @click="removeFile(index)">
                  <i class="bi bi-x-circle"></i>
                </BButton>
              </div>
            </div>
          </div>

          <!-- Excel Sheet Selection (shown when Excel files are selected) -->
          <div v-if="excelSheets.length > 0" class="mt-3 p-3 border rounded bg-light">
            <div class="d-flex align-items-center gap-2 mb-2">
              <i class="bi bi-file-earmark-excel text-success"></i>
              <strong class="small">Excel Sheet Selection</strong>
              <div v-if="loadingSheets" class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Loading sheets...</span>
              </div>
            </div>
            <BFormGroup label="Select sheet to import:" label-size="sm">
              <BFormSelect
                v-model="selectedSheet"
                :options="excelSheets.map(sheet => ({ value: sheet, text: sheet }))"
                size="sm"
                @update:model-value="importForm.sheetName = $event"
              >
                <template #first>
                  <BFormSelectOption :value="''" disabled>-- Select a sheet --</BFormSelectOption>
                </template>
              </BFormSelect>
            </BFormGroup>
            <small class="text-muted d-block mt-1">
              <i class="bi bi-info-circle me-1"></i>
              This Excel file contains {{ excelSheets.length }} sheet(s). Select which sheet to import.
            </small>
          </div>

          <!-- Merge Option (shown when multiple files are selected) -->
          <div v-if="importForm.files.length > 1" class="mt-3 p-3 border rounded bg-light">
            <div class="form-check">
              <input
                class="form-check-input"
                type="checkbox"
                id="mergeFiles"
                v-model="importForm.mergeFiles"
              >
              <label class="form-check-label" for="mergeFiles">
                <strong>Merge files into a single dataset</strong>
              </label>
            </div>
            <small class="text-muted d-block mt-1">
              <i class="bi bi-info-circle me-1"></i>
              When enabled, all files will be combined into one dataset. The dataset name above will be used for the merged result.
              If disabled, each file will be imported as a separate dataset.
            </small>
            <div v-if="importForm.mergeFiles" class="mt-2">
              <BFormGroup label="Merge Strategy" label-size="sm">
                <BFormSelect v-model="importForm.mergeStrategy" size="sm" :options="[
                  { value: 'union', text: 'Union — keep all columns, fill missing with null' },
                  { value: 'intersection', text: 'Intersection — keep only common columns' },
                  { value: 'strict', text: 'Strict — fail if columns don\'t match exactly' },
                ]"></BFormSelect>
              </BFormGroup>
            </div>
          </div>

          <!-- Import Progress -->
          <div v-if="importProgress.length > 0" class="mt-3">
            <div class="fw-bold mb-2">Import Progress</div>
            <div
              v-for="(progress, index) in importProgress"
              :key="index"
              class="import-progress-item d-flex align-items-center gap-2 p-2 border rounded mb-2"
            >
              <div v-if="progress.status === 'pending'" class="spinner-border spinner-border-sm" role="status"></div>
              <i v-else-if="progress.status === 'success'" class="bi bi-check-circle-fill text-success"></i>
              <i v-else-if="progress.status === 'error'" class="bi bi-x-circle-fill text-danger"></i>
              <div class="flex-grow-1">
                <div class="small">{{ progress.fileName }}</div>
                <div v-if="progress.message" class="text-muted" style="font-size: 0.75rem;">{{ progress.message }}</div>
              </div>
            </div>
          </div>

          <!-- Import Options -->
          <div class="mt-3 p-3 border rounded">
            <div class="fw-bold mb-2">Import Options</div>
            <div class="mb-2">
              <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" id="autoMode" :value="true" v-model="importForm.autoDetect">
                <label class="form-check-label" for="autoMode">Auto (recommended)</label>
              </div>
              <div class="form-check form-check-inline">
                <input class="form-check-input" type="radio" id="manualMode" :value="false" v-model="importForm.autoDetect">
                <label class="form-check-label" for="manualMode">Manual</label>
              </div>
            </div>

            <div v-if="importForm.autoDetect === false && !hasParquetFile" class="mt-2 ps-2 border-start">
              <div class="mb-2">
                <label class="form-label">Has Header:</label>
                <div class="form-check">
                  <input class="form-check-input" type="radio" id="hasHeaderYes" :value="true" v-model="importForm.hasHeader">
                  <label class="form-check-label" for="hasHeaderYes">Yes</label>
                </div>
                <div class="form-check">
                  <input class="form-check-input" type="radio" id="hasHeaderNo" :value="false" v-model="importForm.hasHeader">
                  <label class="form-check-label" for="hasHeaderNo">No</label>
                </div>
              </div>
              <div class="mt-2">
                <label class="form-label">Delimiter:</label>
                <select class="form-select" v-model="importForm.delimiter">
                  <option value=",">Comma (,)</option>
                  <option value=";">Semicolon (;)</option>
                  <option value="	">Tab</option>
                  <option value="|">Pipe (|)</option>
                </select>
              </div>
            </div>
            <div v-if="hasParquetFile" class="mt-2 small text-muted">
              <i class="bi bi-info-circle me-1"></i>
              Parquet files don't require delimiter or header options.
            </div>
          </div>
          <div class="mt-3 text-end">
            <BButton v-if="!importComplete" variant="primary" :loading="importing" :disabled="importForm.files.length === 0" @click="handleImport">
              <i class="bi bi-upload me-1"></i> Import {{ importForm.files.length > 0 ? `(${importForm.files.length} files)` : '' }}
            </BButton>
            <BButton v-else variant="secondary" @click="showImportModal = false">
              <i class="bi bi-x-circle me-1"></i> Close
            </BButton>
          </div>
        </div>

        <!-- Database Import -->
        <div v-if="importTab === 'database'">
          <BFormGroup label="Dataset Name">
            <BFormInput v-model="dbImportForm.name" placeholder="My Dataset"></BFormInput>
          </BFormGroup>
          <div class="row g-2 mt-1">
            <div class="col-4">
              <BFormGroup label="Database Type" label-size="sm">
                <BFormSelect v-model="dbImportForm.db_type" :options="dbTypeOptions" size="sm"></BFormSelect>
              </BFormGroup>
            </div>
            <div v-if="dbImportForm.db_type !== 'sqlite'" class="col-5">
              <BFormGroup label="Host" label-size="sm">
                <BFormInput v-model="dbImportForm.host" size="sm" placeholder="localhost"></BFormInput>
              </BFormGroup>
            </div>
            <div v-if="dbImportForm.db_type !== 'sqlite'" class="col-3">
              <BFormGroup label="Port" label-size="sm">
                <BFormInput v-model.number="dbImportForm.port" type="number" size="sm"></BFormInput>
              </BFormGroup>
            </div>
          </div>
          <div v-if="dbImportForm.db_type !== 'sqlite'" class="row g-2 mt-1">
            <div class="col-6">
              <BFormGroup label="Username" label-size="sm">
                <BFormInput v-model="dbImportForm.username" size="sm" placeholder="user"></BFormInput>
              </BFormGroup>
            </div>
            <div class="col-6">
              <BFormGroup label="Password" label-size="sm">
                <BFormInput v-model="dbImportForm.password" type="password" size="sm"></BFormInput>
              </BFormGroup>
            </div>
          </div>

          <div class="row g-2 mt-1">
            <div :class="dbImportForm.db_type === 'sqlite' ? 'col-12' : 'col-6'">
              <BFormGroup label="Database" label-size="sm">
                <BFormInput v-model="dbImportForm.database" size="sm" :placeholder="dbImportForm.db_type === 'sqlite' ? '/path/to/database.db' : 'mydb'"></BFormInput>
              </BFormGroup>
            </div>
            
            <div v-if="dbImportForm.db_type === 'postgresql' || dbImportForm.db_type === 'mysql'" class="col-6">
              <BFormGroup label="SSL Mode" label-size="sm">
                <BFormSelect v-model="dbImportForm.sslmode" :options="sslmodeOptions" size="sm"></BFormSelect>
              </BFormGroup>
            </div>
          </div>
          

          <!-- Saved connections -->
          <div class="d-flex gap-2 mt-2">
            <BButton size="sm" variant="outline-success" @click="saveDbConnection" :disabled="!dbImportForm.host || !dbImportForm.database">
              <i class="bi bi-save me-1"></i> Save
            </BButton>
            <BFormSelect v-if="savedConnections.length" v-model="selectedConnection" :options="savedConnectionOptions" size="sm" style="max-width: 200px;" @update:model-value="loadSavedConnection"></BFormSelect>
            <BButton v-if="selectedConnection" size="sm" variant="outline-danger" @click="deleteSavedConnection">
              <i class="bi bi-trash"></i>
            </BButton>
          </div>

          <!-- Test Connection -->
          <div class="d-flex gap-2 mt-2">
            <BButton size="sm" variant="outline-primary" :loading="dbTesting" @click="testDbConnection">
              <i class="bi bi-plug me-1"></i> Test Connection
            </BButton>
            <span v-if="dbTestResult" :class="dbTestResult.success ? 'text-success' : 'text-danger'" class="small align-self-center">
              <i class="bi me-1" :class="dbTestResult.success ? 'bi-check-circle' : 'bi-x-circle'"></i>
              {{ dbTestResult.message }}
            </span>
          </div>

          <!-- Table Selection -->
          <div v-if="dbTables.length" class="mt-3">
            <BFormGroup label="Select Table" label-size="sm">
              <BFormSelect v-model="dbImportForm.table" :options="dbTableOptions" size="sm"></BFormSelect>
            </BFormGroup>
          </div>
          <div v-else-if="dbImportForm.db_type === 'sqlite' && dbTestResult?.success" class="mt-3">
            <div class="alert alert-info py-2 small">
              <i class="bi bi-info-circle me-1"></i>
              No tables found in the SQLite database. Make sure the database file exists and contains tables.
            </div>
            <BFormGroup label="Table Name (manual entry)" label-size="sm">
              <BFormInput v-model="dbImportForm.table" size="sm" placeholder="Enter table name"></BFormInput>
            </BFormGroup>
          </div>

          <div class="mt-3 text-end">
            <BButton variant="primary" :loading="importing" :disabled="!dbImportForm.name || !dbImportForm.table" @click="handleDbImport">
              <i class="bi bi-download me-1"></i> Import
            </BButton>
          </div>
        </div>
      </div>
      <template #footer><span></span></template>
    </BModal>

    <!-- Rename Dataset Modal -->
    <BModal v-model="showRenameModal" title="Rename Dataset">
      <BFormGroup label="Name" label-for="rename-ds-name">
        <BFormInput id="rename-ds-name" v-model="renameDatasetName" required></BFormInput>
      </BFormGroup>
      <BFormGroup label="Description" label-for="rename-ds-desc">
        <BFormTextarea id="rename-ds-desc" v-model="renameDatasetDesc" rows="2"></BFormTextarea>
      </BFormGroup>
      <template #footer>
        <BButton @click="showRenameModal = false">Cancel</BButton>
        <BButton variant="primary" :loading="renamingDataset" @click="renameDataset">Save</BButton>
      </template>
    </BModal>

    <!-- Profile Modal -->
    <BModal v-model="showProfileModal" title="Data Profile" size="lg">
      <div v-if="profileLoading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="text-muted mt-2">Loading profile…</p>
      </div>
      <div v-else-if="profileData">
        <div class="row g-3">
          <div v-for="col in profileData.columns" :key="col.name" class="col-md-6">
            <div class="card h-100">
              <div class="card-body py-2 px-3">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <strong class="small">{{ col.name }}</strong>
                  <span class="badge bg-light text-dark">{{ col.dtype }}</span>
                </div>
                <div class="small text-muted">
                  <span v-if="col.null_count > 0" class="text-danger me-2">
                    {{ col.null_count }} nulls ({{ col.null_percent }}%)
                  </span>
                  <span>{{ col.unique_count }} unique</span>
                  <span class="ms-2">Quality: {{ col.quality_score }}%</span>
                </div>
                <div v-if="col.stats?.top_values?.length" class="mt-1">
                  <small class="text-muted">Top: </small>
                  <small v-for="(v, i) in col.stats.top_values.slice(0, 3)" :key="i" class="badge bg-light text-dark me-1">{{ v.value }} ({{ v.count }})</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <BButton variant="primary" @click="showProfileModal = false">Close</BButton>
      </template>
    </BModal>

    <!-- Export Modal -->
    <BModal v-model="showExportModal" title="Export Dataset" size="lg">
      <div class="p-3">
        <!-- Tabs -->
        <ul class="nav nav-pills mb-3">
          <li class="nav-item">
            <button class="nav-link" :class="{ active: exportTab === 'file' }" @click="exportTab = 'file'">
              <i class="bi bi-file-earmark-arrow-down me-1"></i> File
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link" :class="{ active: exportTab === 'database' }" @click="exportTab = 'database'">
              <i class="bi bi-database me-1"></i> Database
            </button>
          </li>
        </ul>

        <!-- File Export -->
        <div v-if="exportTab === 'file'">
          <BFormGroup label="Format" label-for="export-format">
            <BFormSelect id="export-format" v-model="exportFormat" :options="[
              { value: 'csv', text: 'CSV (.csv)' },
              { value: 'json', text: 'JSON (.json)' },
              { value: 'tsv', text: 'TSV (.tsv)' },
              { value: 'excel', text: 'Excel (.xlsx)' },
              { value: 'parquet', text: 'Parquet (.parquet)' },
            ]"></BFormSelect>
          </BFormGroup>
          <BFormGroup label="Rows" label-for="export-limit" class="mt-2">
            <BFormSelect id="export-limit" v-model="exportLimit" :options="[
              { value: 0, text: 'All rows' },
              { value: 10, text: 'First 10' },
              { value: 50, text: 'First 50' },
              { value: 100, text: 'First 100' },
              { value: 500, text: 'First 500' },
              { value: 1000, text: 'First 1000' },
            ]"></BFormSelect>
          </BFormGroup>
          <div class="mt-3 text-end">
            <BButton variant="primary" @click="downloadExport">
              <i class="bi bi-download me-1"></i> Download
            </BButton>
          </div>
        </div>

        <!-- Database Export -->
        <div v-if="exportTab === 'database'">
          <div class="row g-2 mt-1">
            <div class="col-4">
              <BFormGroup label="Database Type" label-size="sm">
                <BFormSelect v-model="dbExportForm.db_type" :options="dbTypeOptions" size="sm"></BFormSelect>
              </BFormGroup>
            </div>
            <div v-if="dbExportForm.db_type !== 'sqlite'" class="col-5">
              <BFormGroup label="Host" label-size="sm">
                <BFormInput v-model="dbExportForm.host" size="sm" placeholder="localhost"></BFormInput>
              </BFormGroup>
            </div>
            <div v-if="dbExportForm.db_type !== 'sqlite'" class="col-3">
              <BFormGroup label="Port" label-size="sm">
                <BFormInput v-model.number="dbExportForm.port" type="number" size="sm"></BFormInput>
              </BFormGroup>
            </div>
          </div>
          <div v-if="dbExportForm.db_type !== 'sqlite'" class="row g-2 mt-1">
            <div class="col-6">
              <BFormGroup label="Username" label-size="sm">
                <BFormInput v-model="dbExportForm.username" size="sm" placeholder="user"></BFormInput>
              </BFormGroup>
            </div>
            <div class="col-6">
              <BFormGroup label="Password" label-size="sm">
                <BFormInput v-model="dbExportForm.password" type="password" size="sm"></BFormInput>
              </BFormGroup>
            </div>
          </div>

          <div class="row g-2 mt-1">
            <div :class="dbExportForm.db_type === 'sqlite' ? 'col-12' : 'col-6'">
              <BFormGroup label="Database" label-size="sm">
                <BFormInput v-model="dbExportForm.database" size="sm" :placeholder="dbExportForm.db_type === 'sqlite' ? '/path/to/database.db' : 'mydb'"></BFormInput>
              </BFormGroup>
            </div>
            
            <div v-if="dbExportForm.db_type === 'postgresql' || dbExportForm.db_type === 'mysql'" class="col-6">
              <BFormGroup label="SSL Mode" label-size="sm">
                <BFormSelect v-model="dbExportForm.sslmode" :options="sslmodeOptions" size="sm"></BFormSelect>
              </BFormGroup>
            </div>
          </div>

          <!-- Test Connection -->
          <div class="d-flex gap-2 mt-2">
            <BButton size="sm" variant="outline-primary" :loading="dbExportTesting" @click="testDbExportConnection">
              <i class="bi bi-plug me-1"></i> Test Connection
            </BButton>
            <span v-if="dbExportTestResult" :class="dbExportTestResult.success ? 'text-success' : 'text-danger'" class="small align-self-center">
              <i class="bi me-1" :class="dbExportTestResult.success ? 'bi-check-circle' : 'bi-x-circle'"></i>
              {{ dbExportTestResult.message }}
            </span>
          </div>

          <!-- Mode Selection -->
          <div class="mt-3">
            <BFormGroup label="Export Mode" label-size="sm">
              <BFormSelect v-model="dbExportForm.mode" size="sm" :options="[
                { value: 'create', text: 'Create new table' },
                { value: 'append', text: 'Append to existing table' },
              ]"></BFormSelect>
            </BFormGroup>
          </div>

          <!-- Table Selection (for append mode) -->
          <div v-if="dbExportForm.mode === 'append' && dbExportTables.length" class="mt-2">
            <BFormGroup label="Select Table" label-size="sm">
              <BFormSelect v-model="dbExportForm.table" :options="dbExportTableOptions" size="sm"></BFormSelect>
            </BFormGroup>
          </div>

          <!-- Table Name (for create mode) -->
          <div v-if="dbExportForm.mode === 'create'" class="mt-2">
            <BFormGroup label="Table Name" label-size="sm">
              <BFormInput v-model="dbExportForm.table" size="sm" placeholder="my_table"></BFormInput>
            </BFormGroup>
            <BFormGroup label="If Table Exists" label-size="sm" class="mt-2">
              <BFormSelect v-model="dbExportForm.if_exists" size="sm" :options="[
                { value: 'fail', text: 'Fail (error)' },
                { value: 'replace', text: 'Replace (drop and recreate)' },
                { value: 'append', text: 'Append (add rows)' },
              ]"></BFormSelect>
            </BFormGroup>
          </div>

          <div class="mt-3 text-end">
            <BButton variant="primary" :loading="dbExporting" :disabled="!dbExportForm.table" @click="handleDbExport">
              <i class="bi bi-upload me-1"></i> Export
            </BButton>
          </div>
        </div>
      </div>
      <template #footer><span></span></template>
    </BModal>

    <!-- Preview Modal -->
    <BModal v-model="showPreviewModal" :title="(selectedDataset?.name || 'Dataset') + ' - Preview'" size="xl">
      <BFormGroup label="Rows to Show">
        <BFormSelect v-model="previewLimit" :options="previewLimitOptions"></BFormSelect>
      </BFormGroup>
      <BTable :items="previewData" :fields="previewColumns" :per-page="previewLimit" bordered striped hover></BTable>
      <template #footer>
        <BButton variant="primary" @click="showPreviewModal = false">Close</BButton>
      </template>
    </BModal>

    <!-- Merge Datasets Modal -->
    <BModal v-model="showMergeModal" title="Merge Datasets" size="md">
      <div class="alert alert-info py-2 small mb-3">
        <i class="bi bi-info-circle me-1"></i>
        Combine {{ selectedDatasetIds.length }} datasets into a new dataset.
      </div>
      <BFormGroup label="New dataset name" label-size="sm">
        <BFormInput v-model="mergeName" size="sm" placeholder="Merged Dataset"></BFormInput>
      </BFormGroup>
      <BFormGroup label="Strategy" label-size="sm" class="mt-2">
        <BFormSelect v-model="mergeStrategy" size="sm" :options="[
          { value: 'union', text: 'Union — keep all columns, fill missing with null' },
          { value: 'intersection', text: 'Intersection — keep only common columns' },
          { value: 'strict', text: 'Strict — fail if columns don\'t match exactly' },
        ]"></BFormSelect>
      </BFormGroup>
      <div class="mt-2 small text-muted">
        Selected: {{ selectedDatasetIds.map(id => datasets.find(d => d.id === id)?.name || id).join(', ') }}
      </div>
      <template #footer>
        <BButton variant="outline-secondary" @click="showMergeModal = false">Cancel</BButton>
        <BButton variant="primary" :loading="merging" :disabled="!mergeName" @click="applyMerge">
          <i class="bi bi-arrows-collapse me-1"></i>Merge
        </BButton>
      </template>
    </BModal>

    <!-- Bulk Delete Confirmation Modal -->
    <BModal v-model="showBulkDeleteModal" title="Delete Datasets" size="md">
      <div class="alert alert-danger py-2 small mb-3">
        <i class="bi bi-exclamation-triangle me-1"></i>
        Are you sure you want to delete {{ selectedDatasetIds.length }} dataset(s)? This action cannot be undone.
      </div>
      <div class="small text-muted">
        Selected: {{ selectedDatasetIds.map(id => datasets.find(d => d.id === id)?.name || id).join(', ') }}
      </div>
      <template #footer>
        <BButton variant="outline-secondary" @click="showBulkDeleteModal = false">Cancel</BButton>
        <BButton variant="danger" :loading="deletingBulk" @click="deleteSelectedDatasets">
          <i class="bi bi-trash me-1"></i>Delete
        </BButton>
      </template>
    </BModal>

    <!-- Operation Details Modal -->
    <BModal v-model="showOpDetailsModal" title="Operation Details" size="md">
      <div v-if="selectedOp">
        <div class="mb-3">
          <span class="badge" :class="selectedOp.is_undone ? 'bg-secondary' : 'bg-primary'">
            {{ selectedOp.operation_type }}
          </span>
          <span v-if="selectedOp.is_undone" class="badge bg-warning text-dark ms-1">Undone</span>
          <span v-if="selectedOp.dataset_name" class="badge bg-light text-dark ms-1">{{ selectedOp.dataset_name }}</span>
        </div>
        <div class="mb-2">
          <small class="text-muted">Date</small>
          <div>{{ formatDate(selectedOp.created_at) }}</div>
        </div>
        <div class="mb-2">
          <small class="text-muted">ID</small>
          <div><code class="small">{{ selectedOp.id }}</code></div>
        </div>
        <div v-if="selectedOp.operation_params">
          <small class="text-muted">Parameters</small>
          <pre class="bg-light p-2 rounded small mb-0" style="max-height: 200px; overflow-y: auto;">{{ formatOpParamsPretty(selectedOp.operation_params) }}</pre>
        </div>
      </div>
      <template #footer>
        <BButton variant="primary" @click="showOpDetailsModal = false">Close</BButton>
      </template>
    </BModal>
  </div>
</template>

<script setup>
import { getApiUrl } from '@/utils/api'
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { BButton, BTab, BTabs, BDropdown, BDropdownItem, BBadge, BModal, BFormGroup, BFormInput, BFormTextarea, BFormFile, BFormSelect, BTable } from 'bootstrap-vue-next'
import DatasetCard from '@/components/DatasetCard.vue'

const route = useRoute()
const router = useRouter()
const apiUrl = getApiUrl()
const toast = useToast()

const projectId = route.params.id
const loading = ref(true)
const activeTab = ref(0)
const project = ref(null)
const operations = ref([])
const showImportModal = ref(false)
watch(showImportModal, (val) => {
  if (!val) {
    importForm.name = ''
    importForm.files = []
    importForm.mergeFiles = false
    importForm.sheetName = ''
    importTab.value = 'file'
    importProgress.value = []
    importComplete.value = false
    excelSheets.value = []
    selectedSheet.value = ''
    loadingSheets.value = false
    dbImportForm.name = ''
    dbImportForm.table = ''
    dbTables.value = []
    dbTestResult.value = null
  }
})

const showPreviewModal = ref(false)
const showRenameModal = ref(false)
const showExportModal = ref(false)
const exportTab = ref('file')
const exportFormat = ref('csv')
const exportLimit = ref(0)

watch(showExportModal, (val) => {
  if (!val) {
    exportTab.value = 'file'
    exportFormat.value = 'csv'
    exportLimit.value = 0
    dbExportForm.table = ''
    dbExportForm.mode = 'create'
    dbExportForm.if_exists = 'fail'
    dbExportTables.value = []
    dbExportTestResult.value = null
  }
})

const dbExportForm = reactive({
  db_type: 'postgresql',
  host: 'localhost',
  port: 5432,
  database: '',
  username: '',
  password: '',
  sslmode: '',
  table: '',
  mode: 'create',
  if_exists: 'fail'
})
const dbExportTesting = ref(false)
const dbExportTestResult = ref(null)
const dbExportTables = ref([])
const dbExporting = ref(false)
const showProfileModal = ref(false)
const profileData = ref(null)
const profileLoading = ref(false)
const showOpDetailsModal = ref(false)
const selectedOp = ref(null)
const showMergeModal = ref(false)
const selectedDatasetIds = ref([])
const mergeName = ref('Merged Dataset')
const mergeStrategy = ref('union')
const merging = ref(false)
const showBulkDeleteModal = ref(false)
const deletingBulk = ref(false)
const renameDatasetId = ref(null)
const renameDatasetName = ref('')
const renameDatasetDesc = ref('')
const renamingDataset = ref(false)
const importTab = ref('file')
const importing = ref(false)
const dbTesting = ref(false)
const dbTestResult = ref(null)
const dbTables = ref([])

// Saved connections (localStorage)
const savedConnections = ref(JSON.parse(localStorage.getItem('dbConnections') || '[]'))
const selectedConnection = ref(null)

const savedConnectionOptions = computed(() => [
  { value: null, text: 'Load connection…' },
  ...savedConnections.value.map((c, i) => ({ value: i, text: `${c.name} (${c.db_type})` }))
])

function saveDbConnection() {
  const name = dbImportForm.name || `${dbImportForm.db_type}@${dbImportForm.host}`
  const conn = {
    name,
    db_type: dbImportForm.db_type,
    host: dbImportForm.host,
    port: dbImportForm.port,
    database: dbImportForm.database,
    username: dbImportForm.username,
    sslmode: dbImportForm.sslmode,
  }
  savedConnections.value.push(conn)
  localStorage.setItem('dbConnections', JSON.stringify(savedConnections.value))
  toast.success('Connection saved')
}

function loadSavedConnection(index) {
  if (index === null || index === undefined) return
  const conn = savedConnections.value[index]
  if (!conn) return
  Object.assign(dbImportForm, { ...conn, password: '', table: '' })
  dbTables.value = []
  dbTestResult.value = null
}

function deleteSavedConnection() {
  if (selectedConnection.value === null) return
  savedConnections.value.splice(selectedConnection.value, 1)
  localStorage.setItem('dbConnections', JSON.stringify(savedConnections.value))
  selectedConnection.value = null
}

const dbTypeOptions = [
  { value: 'postgresql', text: 'PostgreSQL' },
  { value: 'mysql', text: 'MySQL' },
  { value: 'sqlite', text: 'SQLite' },
  { value: 'oracle', text: 'Oracle' },
  { value: 'mssql', text: 'SQL Server' },
]

const sslmodeOptions = [
  { value: '', text: 'None' },
  { value: 'disable', text: 'Disable' },
  { value: 'allow', text: 'Allow' },
  { value: 'prefer', text: 'Prefer' },
  { value: 'require', text: 'Require' },
  { value: 'verify-ca', text: 'Verify CA' },
  { value: 'verify-full', text: 'Verify Full' },
]

const dbImportForm = reactive({
  name: '',
  db_type: 'postgresql',
  host: 'localhost',
  port: 5432,
  database: '',
  username: '',
  password: '',
  sslmode: '',
  table: '',
})

const dbTableOptions = computed(() => [
  { value: '', text: 'Select table…', disabled: true },
  ...dbTables.value.map(t => ({ value: t, text: t }))
])

// Update port when db_type changes
watch(() => dbImportForm.db_type, (type) => {
  const defaultPorts = { postgresql: 5432, mysql: 3306, sqlite: 0, oracle: 1521, mssql: 1433 }
  dbImportForm.port = defaultPorts[type] || 5432
  if (type === 'sqlite') dbImportForm.host = ''
})
const showAssistantModal = ref(false)
const selectedDataset = ref(null)
const previewLimit = ref(10)
const previewData = ref([])

const previewLimitOptions = [
  { value: 10, text: '10 rows' },
  { value: 25, text: '25 rows' },
  { value: 50, text: '50 rows' },
  { value: 100, text: '100 rows' }
]

const importForm = reactive({
  name: '',
  files: [],
  autoDetect: true,
  hasHeader: true,
  delimiter: ',',
  mergeFiles: false,
  mergeStrategy: 'union',
  sheetName: ''
})

const isDragging = ref(false)
const fileInput = ref(null)
const importProgress = ref([])
const importComplete = ref(false)
const excelSheets = ref([])
const selectedSheet = ref('')
const loadingSheets = ref(false)

const autoModeOptions = [
  { value: true, text: 'Auto (recommended)' },
  { value: false, text: 'Manual' }
]

const headerOptions = [
  { value: true, text: 'Yes' },
  { value: false, text: 'No' }
]

const delimiterOptions = [
  { value: ',', text: 'Comma (,)' },
  { value: ';', text: 'Semicolon (;)' },
  { value: '\t', text: 'Tab' },
  { value: '|', text: 'Pipe (|)' }
]

const previewColumns = computed(() => {
  if (previewData.value.length === 0) return []
  return Object.keys(previewData.value[0]).map(key => ({
    key: key,
    label: key
  }))
})

const hasParquetFile = computed(() => {
  return importForm.files.some(file => {
    const ext = file.name.split('.').pop().toLowerCase()
    return ext === 'parquet'
  })
})

onMounted(async () => {
  await fetchProject()
  await fetchDatasets()
  await fetchOperations() // Load operations on mount
  loading.value = false

  // Auto-open import modal if navigated from dashboard "Import Data" shortcut
  if (route.query.import === 'true') {
    showImportModal.value = true
    router.replace({ query: {} })
  }
})

// Watch for tab changes to refresh operations when Operations tab is active
watch(activeTab, async (newTab) => {
  if (newTab === 1) { // Operations tab
    // Already loaded in onMounted, but refresh to get latest
    operations.value = [] 
    await fetchOperations()
  }
})

async function fetchProject() {
  try {
    const res = await fetch(`${apiUrl}/api/projects/${projectId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      project.value = await res.json()
    }
  } catch (e) {
    console.error(e)
  }
}

const datasets = ref([])
const datasetTotal = ref(0)
const datasetPage = ref(1)
const datasetPageSize = ref(12)

async function fetchDatasets() {
  try {
    const res = await fetch(`${apiUrl}/api/datasets?project_id=${projectId}&page=${datasetPage.value}&page_size=${datasetPageSize.value}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      datasets.value = data.datasets || data || []
      datasetTotal.value = data.total || datasets.value.length
    }
  } catch (e) {
    console.error(e)
  }
}

async function fetchOperations() {
  try {
    const res = await fetch(`${apiUrl}/api/datasets?project_id=${projectId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      const datasetsList = data.datasets || data || []
      // Get operations for each dataset
      const allOps = []
      for (const ds of datasetsList) {
        const opsRes = await fetch(`${apiUrl}/api/datasets/${ds.id}/operations`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        })
        if (opsRes.ok) {
          const opsData = await opsRes.json()
          const opsList = opsData.operations || opsData || []
          allOps.push(...opsList.map(op => ({ ...op, dataset_name: ds.name })))
        }
      }
      // Sort by date descending
      allOps.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      operations.value = allOps
    }
  } catch (e) {
    console.error(e)
  }
}

function triggerFileInput() {
  fileInput.value?.click()
}

function handleDrop(e) {
  isDragging.value = false
  const files = Array.from(e.dataTransfer.files)
  addFiles(files)
}

function handleFileSelect(e) {
  const files = Array.from(e.target.files)
  addFiles(files)
}

function addFiles(files) {
  const validFiles = files.filter(file => {
    const ext = file.name.split('.').pop().toLowerCase()
    return ['csv', 'tsv', 'txt', 'xlsx', 'xls', 'parquet'].includes(ext)
  })
  importForm.files.push(...validFiles)
  
  // Auto-populate dataset name from first file if name is empty
  if (!importForm.name && validFiles.length > 0) {
    const firstFileName = validFiles[0].name
    // Remove file extension
    const nameWithoutExt = firstFileName.replace(/\.[^/.]+$/, '')
    importForm.name = nameWithoutExt
  }
  
  // Check if any Excel files were added and fetch sheets
  const excelFiles = validFiles.filter(file => {
    const ext = file.name.split('.').pop().toLowerCase()
    return ['xlsx', 'xls'].includes(ext)
  })
  
  if (excelFiles.length > 0) {
    fetchExcelSheets(excelFiles[0])
  }
}

async function fetchExcelSheets(file) {
  loadingSheets.value = true
  excelSheets.value = []
  selectedSheet.value = ''
  
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const res = await fetch(`${apiUrl}/api/datasets/import/excel/sheets`, {
      method: 'POST',
      body: formData,
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    
    if (res.ok) {
      const data = await res.json()
      excelSheets.value = data.sheets || []
      
      // Auto-select first sheet if only one sheet available
      if (excelSheets.value.length === 1) {
        selectedSheet.value = excelSheets.value[0]
        importForm.sheetName = excelSheets.value[0]
      }
    }
  } catch (e) {
    console.error('Failed to fetch Excel sheets:', e)
  } finally {
    loadingSheets.value = false
  }
}

function removeFile(index) {
  importForm.files.splice(index, 1)
  
  // Reset sheet selection if no Excel files remain
  const hasExcelFiles = importForm.files.some(file => {
    const ext = file.name.split('.').pop().toLowerCase()
    return ['xlsx', 'xls'].includes(ext)
  })
  
  if (!hasExcelFiles) {
    excelSheets.value = []
    selectedSheet.value = ''
    importForm.sheetName = ''
  }
  
  // Reset dataset name if no files remain
  if (importForm.files.length === 0) {
    importForm.name = ''
  }
}

function clearFiles() {
  importForm.files = []
  importForm.name = ''
  excelSheets.value = []
  selectedSheet.value = ''
  importForm.sheetName = ''
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

async function handleImport() {
  if (importForm.files.length === 0) return
  
  importing.value = true
  importComplete.value = false
  importProgress.value = importForm.files.map(file => ({
    fileName: file.name,
    status: 'pending',
    message: null
  }))

  try {
    const formData = new FormData()
    formData.append('project_id', projectId)
    if (importForm.name) formData.append('name', importForm.name)
    formData.append('auto_detect', importForm.autoDetect.toString())
    formData.append('delimiter', importForm.delimiter)
    formData.append('has_header', importForm.hasHeader.toString())
    if (importForm.sheetName) formData.append('sheet_name', importForm.sheetName)
    
    // Use single endpoint for one file, multiple endpoint for multiple files
    const isSingleFile = importForm.files.length === 1
    const endpoint = isSingleFile ? 'single' : 'multiple'
    
    if (isSingleFile) {
      formData.append('file', importForm.files[0])
    } else {
      importForm.files.forEach(file => {
        formData.append('files', file)
      })
      if (importForm.mergeFiles) formData.append('merge_strategy', importForm.mergeStrategy)
    }

    const res = await fetch(`${apiUrl}/api/datasets/import/${endpoint}`, {
      method: 'POST',
      body: formData,
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    
    if (res.ok) {
      const data = await res.json()
      if (isSingleFile) {
        // Single file response
        importProgress.value[0] = {
          fileName: importForm.files[0].name,
          status: 'success',
          message: `Imported ${data.row_count} rows`
        }
      } else {
        // Multiple files response
        data.results.forEach((result, index) => {
          importProgress.value[index] = {
            fileName: result.file_name,
            status: result.success ? 'success' : 'error',
            message: result.message
          }
        })
      }
      
      // Refresh datasets list
      await fetchDatasets()
      importComplete.value = true
    }
  } catch (e) {
    console.error(e)
  } finally {
    importing.value = false
  }
}

async function testDbConnection() {
  dbTesting.value = true
  dbTestResult.value = null
  dbTables.value = []
  dbImportForm.table = ''
  try {
    const res = await fetch(`${apiUrl}/api/datasets/import/db/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(dbImportForm)
    })
    if (res.ok) {
      dbTestResult.value = { success: true, message: 'Connected!' }
      await fetchDbTables()
    } else {
      const err = await res.json()
      dbTestResult.value = { success: false, message: err.detail || 'Connection failed' }
    }
  } catch (e) {
    dbTestResult.value = { success: false, message: e.message }
  } finally {
    dbTesting.value = false
  }
}

async function fetchDbTables() {
  try {
    const res = await fetch(`${apiUrl}/api/datasets/import/db/tables`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(dbImportForm)
    })
    if (res.ok) {
      const data = await res.json()
      dbTables.value = data.tables || []
    }
  } catch { /* silent */ }
}

async function handleDbImport() {
  if (!dbImportForm.name || !dbImportForm.table) return
  importing.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/import/db`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ ...dbImportForm, project_id: projectId })
    })
    if (res.ok) {
      const data = await res.json()
      showImportModal.value = false
      dbTables.value = []
      dbTestResult.value = null
      await fetchDatasets()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Import failed')
    }
  } catch (e) {
    toast.error(e.message)
  } finally {
    importing.value = false
  }
}

async function previewDataset(dataset) {
  selectedDataset.value = dataset
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${dataset.id}/preview?limit=${previewLimit.value}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      previewData.value = data.preview_data || []
      showPreviewModal.value = true
    }
  } catch (e) {
    console.error(e)
  }
}

function openRenameModal(dataset) {
  renameDatasetId.value = dataset.id
  renameDatasetName.value = dataset.name
  renameDatasetDesc.value = dataset.description || ''
  showRenameModal.value = true
}

async function renameDataset() {
  if (!renameDatasetName.value.trim()) return
  renamingDataset.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${renameDatasetId.value}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ name: renameDatasetName.value, description: renameDatasetDesc.value })
    })
    if (res.ok) {
      showRenameModal.value = false
      await fetchDatasets()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed to rename')
    }
  } catch (e) { toast.error(e.message) }
  finally { renamingDataset.value = false }
}

async function deleteDataset(dataset) {
  try {
    await fetch(`${apiUrl}/api/datasets/${dataset.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    await fetchDatasets()
  } catch (e) {
    console.error(e)
  }
}

function exportDataset(dataset) {
  selectedDataset.value = dataset
  exportFormat.value = 'csv'
  exportLimit.value = 0
  showExportModal.value = true
}

function downloadExport() {
  if (!selectedDataset.value) return
  const params = new URLSearchParams({ format: exportFormat.value })
  if (exportLimit.value > 0) params.set('limit', exportLimit.value)

  // Use fetch with auth header instead of window.open (which doesn't send auth)
  fetch(`${apiUrl}/api/datasets/${selectedDataset.value.id}/export?${params}`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  })
    .then(res => {
      if (!res.ok) throw new Error(`Export failed (${res.status})`)
      const disposition = res.headers.get('Content-Disposition') || ''
      const match = disposition.match(/filename="(.+?)"/)
      let filename = match ? match[1] : null
      
      // If no filename from header, construct it based on format
      if (!filename) {
        const baseName = selectedDataset.value.name || 'export'
        const safeName = baseName.replace(/[^a-zA-Z0-9\-_ ]/g, '_')
        filename = `${safeName}.${exportFormat.value}`
      }
      
      return res.blob().then(blob => ({ blob, filename }))
    })
    .then(({ blob, filename }) => {
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      URL.revokeObjectURL(url)
    })
    .catch(e => { toast.error(e.message) })

  showExportModal.value = false
}

// Update port when db_type changes for export
watch(() => dbExportForm.db_type, (type) => {
  const defaultPorts = { postgresql: 5432, mysql: 3306, sqlite: 0, oracle: 1521, mssql: 1433 }
  dbExportForm.port = defaultPorts[type] || 5432
  if (type === 'sqlite') dbExportForm.host = ''
})

async function testDbExportConnection() {
  dbExportTesting.value = true
  dbExportTestResult.value = null
  dbExportTables.value = []
  dbExportForm.table = ''
  try {
    const res = await fetch(`${apiUrl}/api/datasets/import/db/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(dbExportForm)
    })
    if (res.ok) {
      dbExportTestResult.value = { success: true, message: 'Connected!' }
      await fetchDbExportTables()
    } else {
      const err = await res.json()
      dbExportTestResult.value = { success: false, message: err.detail || 'Connection failed' }
    }
  } catch (e) {
    dbExportTestResult.value = { success: false, message: e.message }
  } finally {
    dbExportTesting.value = false
  }
}

async function fetchDbExportTables() {
  try {
    const res = await fetch(`${apiUrl}/api/datasets/import/db/tables`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(dbExportForm)
    })
    if (res.ok) {
      const data = await res.json()
      dbExportTables.value = data.tables || []
    }
  } catch { /* silent */ }
}

const dbExportTableOptions = computed(() => [
  { value: '', text: 'Select table…', disabled: true },
  ...dbExportTables.value.map(t => ({ value: t, text: t }))
])

async function handleDbExport() {
  if (!selectedDataset.value || !dbExportForm.table) return
  dbExporting.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${selectedDataset.value.id}/export/db`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(dbExportForm)
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message || 'Exported successfully')
      if (data.warnings && data.warnings.length > 0) {
        data.warnings.forEach(w => toast.warning(w))
      }
      showExportModal.value = false
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Export failed')
    }
  } catch (e) {
    toast.error(e.message)
  } finally {
    dbExporting.value = false
  }
}

function viewDataset(dataset) {
  router.push(`/projects/${projectId}/dataset/${dataset.id}`)
}

function profileDataset(dataset) {
  selectedDataset.value = dataset
  fetchDatasetProfile(dataset.id)
}

async function fetchDatasetProfile(dsId) {
  profileLoading.value = true
  profileData.value = null
  showProfileModal.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${dsId}/profile`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      profileData.value = await res.json()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed to load profile')
    }
  } catch (e) { toast.error(e.message) }
  finally { profileLoading.value = false }
}

function formatNumber(num) {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}

function getOperationClass(opType) {
  const classes = {
    'fillna': 'bg-success',
    'drop_duplicates': 'bg-warning',
    'rename': 'bg-info',
    'remove_columns': 'bg-danger',
    'add_column': 'bg-primary',
    'reorder_columns': 'bg-secondary',
    'deduplicate': 'bg-warning',
    'ai_clean': 'bg-primary',
  }
  return classes[opType] || 'bg-secondary'
}

function getOperationIcon(opType) {
  const icons = {
    'fillna': 'bi bi-droplet',
    'drop_duplicates': 'bi bi-copy',
    'rename': 'bi bi-pencil',
    'remove_columns': 'bi bi-trash',
    'add_column': 'bi bi-plus-circle',
    'reorder_columns': 'bi bi-arrow-left-right',
    'deduplicate': 'bi bi-copy',
    'ai_clean': 'bi bi-stars',
  }
  return icons[opType] || 'bi bi-gear'
}

function formatOperationType(opType) {
  if (!opType) return 'Unknown'
  return opType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function showOpDetails(op) {
  selectedOp.value = op
  showOpDetailsModal.value = true
}

function formatOpParamsPretty(params) {
  if (!params) return ''
  try {
    return JSON.stringify(params, null, 2)
  } catch { return String(params) }
}

function toggleDatasetSelection(id) {
  const idx = selectedDatasetIds.value.indexOf(id)
  if (idx >= 0) selectedDatasetIds.value.splice(idx, 1)
  else selectedDatasetIds.value.push(id)
}

function openMergeModal() {
  mergeName.value = 'Merged Dataset'
  mergeStrategy.value = 'union'
  showMergeModal.value = true
}

async function applyMerge() {
  if (!mergeName.value || selectedDatasetIds.value.length < 2) return
  merging.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/merge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({
        project_id: projectId,
        dataset_ids: selectedDatasetIds.value,
        name: mergeName.value,
        strategy: mergeStrategy.value,
      })
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message || 'Datasets merged')
      showMergeModal.value = false
      selectedDatasetIds.value = []
      await fetchDatasets()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Merge failed')
    }
  } catch (e) { toast.error(e.message) }
  finally { merging.value = false }
}

function confirmBulkDelete() {
  showBulkDeleteModal.value = true
}

async function deleteSelectedDatasets() {
  if (selectedDatasetIds.value.length === 0) return
  deletingBulk.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/bulk-delete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ dataset_ids: selectedDatasetIds.value })
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(`Deleted ${data.deleted_count} dataset(s)`)
      showBulkDeleteModal.value = false
      selectedDatasetIds.value = []
      await fetchDatasets()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Delete failed')
    }
  } catch (e) { toast.error(e.message) }
  finally { deletingBulk.value = false }
}
</script>

<style scoped>
.dataset-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.dataset-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* Operations List */
.operations-list {
  display: flex;
  flex-direction: column;
}

.operation-item {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: background 0.2s ease;
}

.operation-item:last-child {
  border-bottom: none;
}

.operation-item:hover {
  background: rgba(79, 70, 229, 0.03);
}

.operation-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.operation-icon.bg-primary { background: rgba(79, 70, 229, 0.1); }
.operation-icon.bg-success { background: rgba(34, 197, 94, 0.1); }
.operation-icon.bg-warning { background: rgba(249, 115, 22, 0.1); }
.operation-icon.bg-danger { background: rgba(239, 68, 68, 0.1); }
.operation-icon.bg-info { background: rgba(6, 182, 212, 0.1); }
.operation-icon.bg-secondary { background: rgba(107, 114, 128, 0.1); }

/* Drop Zone */
.drop-zone {
  border: 2px dashed #dee2e6;
  cursor: pointer;
  transition: all 0.2s ease;
}

.drop-zone:hover {
  border-color: #6c757d;
  background-color: #f8f9fa;
}

.drop-zone-active {
  border-color: #0d6efd;
  background-color: #e7f1ff;
}

/* File List */
.file-item {
  transition: background 0.2s ease;
}

.file-item:hover {
  background-color: #f8f9fa;
}

/* Import Progress */
.import-progress-item {
  transition: background 0.2s ease;
}

.import-progress-item:hover {
  background-color: #f8f9fa;
}
</style>
