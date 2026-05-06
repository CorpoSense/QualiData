<template>
  <div class="data-viewer">
    <!-- Breadcrumb -->
    <Breadcrumb :items="breadcrumbItems" />
    <!-- Operations Toolbar -->
    <div class="card mb-3">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
          <div class="d-flex align-items-center gap-2">
            <!-- Per-page selector -->
            <select v-model="limit" class="form-select form-select-sm" style="width: auto;">
              <option v-for="opt in limitOptions" :key="opt.value" :value="opt.value">{{ opt.text }}</option>
            </select>
            <span class="text-muted ms-3">{{ totalRows }} total rows</span>
            <BButton size="sm" variant="outline-secondary" @click="refreshData">
              <i class="bi bi-arrow-clockwise me-1"></i> Refresh
            </BButton>
          </div>
          
          <div class="d-flex align-items-center gap-2 flex-wrap">
            <BFormInput v-model="searchQuery" size="sm" placeholder="Search..." style="width: 150px;"></BFormInput>
            <span v-if="hasActiveFilter" class="badge bg-warning text-dark" style="cursor: pointer;" @click="showRowFilterModal = true" title="Click to edit filter">
              <i class="bi bi-funnel-fill me-1"></i>{{ filteredData.length }}/{{ data.length }} rows
            </span>
            <span v-if="hasColumnFilters" class="badge bg-info text-dark" style="cursor: pointer;" @click="clearColumnFilters" title="Click to clear column filters">
              <i class="bi bi-funnel-fill me-1"></i>{{ activeColumnFilterCount }} column filter(s)
            </span>
            <BButton size="sm" variant="info" @click="showProfile = true">
              <i class="bi bi-bar-chart me-1"></i> Profile
            </BButton>
            <BButton size="sm" variant="primary" @click="showPivotModal = true" :disabled="!selectedColumns.length">
              <i class="bi bi-table me-1"></i> Pivot
            </BButton>
            <BButton size="sm" variant="success" @click="showCompare = true">
              <i class="bi bi-columns-gap me-1"></i> Compare
            </BButton>
            <BButton size="sm" variant="secondary" @click="showHistory = !showHistory">
              <i class="bi bi-clock-history me-1"></i> History
            </BButton>
            <BButton size="sm" variant="primary" @click="showAiChat = true">
              <i class="bi bi-chat-dots me-1"></i> AI
            </BButton>
            <BButton size="sm" variant="warning" outline @click="showClipboardImport = true">
              <i class="bi bi-clipboard me-1"></i> Paste
            </BButton>
            <BButton size="sm" variant="warning" outline @click="copyToClipboard">
              <i class="bi bi-clipboard-check me-1"></i> Copy
            </BButton>
          </div>
        </div>

        <!-- Operation Buttons -->
        <div class="d-flex flex-wrap gap-2 align-items-center">
          <BDropdown text="Missing Values" size="sm">
            <BDropdownItem @click="showOpConfirmModal('fillna-drop')">
              <i class="bi bi-trash me-2"></i>Drop rows with nulls
            </BDropdownItem>
            <BDropdownItem @click="showFillnaModal = true">
              <i class="bi bi-pencil me-2"></i>Fill with value…
            </BDropdownItem>
            <BDropdownItem @click="showOpConfirmModal('fillna-mean')">
              <i class="bi bi-calculator me-2"></i>Fill with mean (numeric)
            </BDropdownItem>
            <BDropdownItem @click="showOpConfirmModal('fillna-median')">
              <i class="bi bi-calculator me-2"></i>Fill with median (numeric)
            </BDropdownItem>
            <BDropdownItem @click="showOpConfirmModal('fillna-mode')">
              <i class="bi bi-bar-chart me-2"></i>Fill with mode
            </BDropdownItem>
            <BDropdownItem @click="showOpConfirmModal('fillna-forward')">
              <i class="bi bi-arrow-down me-2"></i>Forward fill
            </BDropdownItem>
            <BDropdownItem @click="showOpConfirmModal('fillna-backward')">
              <i class="bi bi-arrow-up me-2"></i>Backward fill
            </BDropdownItem>
          </BDropdown>

          <BDropdown text="String Ops" size="sm">
            <BDropdownItem @click="showOpConfirmModal('string-strip')">
              <i class="bi bi-type me-2"></i>Trim whitespace
            </BDropdownItem>
            <BDropdownItem @click="showOpConfirmModal('string-lower')">
              <i class="bi bi-type me-2"></i>Lowercase
            </BDropdownItem>
            <BDropdownItem @click="showOpConfirmModal('string-upper')">
              <i class="bi bi-type me-2"></i>Uppercase
            </BDropdownItem>
            <BDropdownItem @click="showOpConfirmModal('string-title')">
              <i class="bi bi-type me-2"></i>Title case
            </BDropdownItem>
            <BDropdownItem @click="showOpConfirmModal('string-capitalize')">
              <i class="bi bi-type me-2"></i>Capitalize
            </BDropdownItem>
      <BDropdownItem @click="openExtractJsonModal" :disabled="selectedColumns.length > 1">
        <i class="bi bi-braces me-2"></i>Extract JSON value…
      </BDropdownItem>
      <BDropdownItem @click="openExtractPatternModal" :disabled="selectedColumns.length > 1">
        <i class="bi bi-regex me-2"></i>Extract pattern…
      </BDropdownItem>
      <BDropdownItem @click="showFindReplaceModal = true">
        <i class="bi bi-arrow-left-right me-2"></i>Find & Replace…
      </BDropdownItem>
      <BDropdownItem @click="openValueMappingModal" :disabled="selectedColumns.length !== 1">
        <i class="bi bi-map me-2"></i>Map Values…
        <span v-if="selectedColumns.length !== 1" class="text-muted small ms-2">(select 1)</span>
      </BDropdownItem>
    </BDropdown>

          <BDropdown text="Date Ops" size="sm">
            <BDropdownItem @click="showOpConfirmModal('datetime-parse-datetime')">
              <i class="bi bi-calendar me-2"></i>Parse datetime
            </BDropdownItem>
            <BDropdownItem @click="showOpConfirmModal('datetime-extract-year')">
              <i class="bi bi-calendar3 me-2"></i>Extract year
            </BDropdownItem>
            <BDropdownItem @click="showOpConfirmModal('datetime-extract-month')">
              <i class="bi bi-calendar3 me-2"></i>Extract month
            </BDropdownItem>
          </BDropdown>

          <BDropdown text="Numeric Ops" size="sm">
            <BDropdownItem @click="showOpConfirmModal('numeric-round')">
              <i class="bi bi-123 me-2"></i>Round numbers
            </BDropdownItem>
            <BDropdownItem @click="showOpConfirmModal('numeric-normalize')">
              <i class="bi bi-percent me-2"></i>Normalize (min-max 0–1)
            </BDropdownItem>
            <BDropdownItem @click="showOpConfirmModal('numeric-standardize')">
              <i class="bi bi-graph-up me-2"></i>Standardize (Z-score)
            </BDropdownItem>
            <BDropdownItem @click="showOpConfirmModal('numeric-robust')">
              <i class="bi bi-shield-check me-2"></i>Robust scale
            </BDropdownItem>
            <BDropdownItem @click="showOpConfirmModal('numeric-outliers')">
              <i class="bi bi-exclamation-triangle me-2"></i>Handle outliers
            </BDropdownItem>
          </BDropdown>

          <BDropdown text="Structure" size="sm">
            <BDropdownItem @click="applyStructuralOp('add_column')">
              <i class="bi bi-plus-circle me-2"></i>Add column
            </BDropdownItem>
            <BDropdownItem @click="applyStructuralOp('rename')" :disabled="selectedColumns.length !== 1">
              <i class="bi bi-pencil-square me-2"></i>Rename column
              <span v-if="selectedColumns.length !== 1" class="text-muted small ms-2">(select 1)</span>
            </BDropdownItem>
            <BDropdownItem @click="applyStructuralOp('drop')">
              <i class="bi bi-trash me-2"></i>Drop column
            </BDropdownItem>
            <BDropdownItem @click="openChangeTypeModal">
              <i class="bi bi-arrow-left-right me-2"></i>Change type
            </BDropdownItem>
            <BDropdownItem @click="openMergeColumnsModal">
              <i class="bi bi-arrows-collapse me-2"></i>Merge columns
            </BDropdownItem>
            <BDropdownItem @click="openSplitColumnModal" :disabled="selectedColumns.length !== 1">
              <i class="bi bi-arrows-expand me-2"></i>Split column
              <span v-if="selectedColumns.length !== 1" class="text-muted small ms-2">(select 1)</span>
            </BDropdownItem>
            <BDropdownItem @click="openCloneColumnModal" :disabled="selectedColumns.length !== 1">
              <i class="bi bi-copy me-2"></i>Clone column
              <span v-if="selectedColumns.length !== 1" class="text-muted small ms-2">(select 1)</span>
            </BDropdownItem>
          </BDropdown>

          <BDropdown text="Dedupe" size="sm">
            <BDropdownItem @click="showOpConfirmModal('remove-duplicates')">
              <i class="bi bi-copy me-2"></i>Remove duplicates
            </BDropdownItem>
            <BDropdownItem @click="showFuzzyMatchModal = true">
              <i class="bi bi-search me-2"></i>Fuzzy match…
            </BDropdownItem>
          </BDropdown>

          <BDropdown text="ML Encode" size="sm">
            <BDropdownItem @click="openEncodingModal('one_hot')">
              <i class="bi bi-grid-3x3-gap me-2"></i>One-Hot Encoding
            </BDropdownItem>
            <BDropdownItem @click="openEncodingModal('label')">
              <i class="bi bi-123 me-2"></i>Label Encoding
            </BDropdownItem>
            <BDropdownItem @click="openEncodingModal('map')">
              <i class="bi bi-arrow-left-right me-2"></i>Map Values
            </BDropdownItem>
            <BDropdownItem @click="openEncodingModal('bin')">
              <i class="bi bi-bar-chart-steps me-2"></i>Binning
            </BDropdownItem>
          </BDropdown>

          <BDropdown text="Rows" size="sm">
            <BDropdownItem @click="showRowFilterModal = true">
              <i class="bi bi-funnel me-2"></i>Filter rows
            </BDropdownItem>
            <BDropdownItem @click="clearRowFilter" v-if="hasActiveFilter">
              <i class="bi bi-x-circle me-2"></i>Clear filter
            </BDropdownItem>
            <BDropdownItem @click="deleteRows('first')" :disabled="!data.length">
              <i class="bi bi-arrow-bar-up me-2"></i>Delete first N rows
            </BDropdownItem>
            <BDropdownItem @click="deleteRows('last')" :disabled="!data.length">
              <i class="bi bi-arrow-bar-down me-2"></i>Delete last N rows
            </BDropdownItem>
            <BDropdownItem @click="deleteRows('range')" :disabled="!data.length">
              <i class="bi bi-arrows-expand me-2"></i>Delete row range
            </BDropdownItem>
            <BDropdownItem @click="deleteVisibleRows" :disabled="!filteredData.length">
              <i class="bi bi-trash me-2"></i>Delete {{ filteredData.length }} visible row(s)
            </BDropdownItem>
            <BDropdownItem v-if="rowSelectMode && selectedRowIndices.length > 0" @click="deleteSelectedRows" variant="danger">
              <i class="bi bi-trash me-2"></i>Delete {{ selectedRowIndices.length }} selected row(s)
            </BDropdownItem>
          </BDropdown>

          <BDropdown text="AI Clean" size="sm">
            <BDropdownItem @click="showStructuralAiModal = true">
              <i class="bi bi-list-task me-2"></i> Structural (Columns)
            </BDropdownItem>
            <BDropdownItem @click="showDataAiModal = true">
              <i class="bi bi-table me-2"></i> Data (Columns + Rows)
            </BDropdownItem>
          </BDropdown>

          <div class="ms-auto d-flex gap-1">
            <BButton size="sm" variant="outline-secondary" :disabled="!canUndo" @click="undo">
              <i class="bi bi-arrow-counterclockwise"></i>
            </BButton>
            <BButton size="sm" variant="outline-secondary" :disabled="!canRedo" @click="redo">
              <i class="bi bi-arrow-clockwise"></i>
            </BButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Selection Bar - click columns in table to select -->
    <div class="d-flex gap-2 mb-3 flex-wrap align-items-center">
      <BBadge :variant="rowSelectMode && selectedRowIndices.length ? 'info' : 'secondary'" pill>{{ (rowSelectMode && selectedRowIndices.length)?selectedRowIndices.length:data.length }} rows</BBadge>
      <BBadge variant="secondary" pill>{{ columns.length }} columns</BBadge>
       <BBadge v-b-tooltip="'Click to show all columns'" v-if="hiddenColumns.length > 0" variant="warning" pill class="cursor-pointer" @click="unhideAllColumns">
         <i class="bi bi-eye-slash me-1"></i>{{ hiddenColumns.length }} hidden
       </BBadge>
      <BBadge variant="warning" pill>{{ nullCount }} nulls</BBadge>
      <!-- Selected columns display -->
      <BBadge v-b-tooltip="'Click to clear selection'" v-if="selectedColumns.length > 0" variant="info" pill class="ms-2 cursor-pointer" @click="selectedColumns = []">
          <i class="bi bi-check2-square me-1"></i>
          {{ selectedColumns.length === 1 ? `1 column: ${selectedColumns[0]}` : `${selectedColumns.length} columns selected` }}
      </BBadge>
      <BButton v-b-tooltip="'Click to select all columns'" size="sm" variant="outline-secondary" @click="selectedColumns = columns.map(c => c.field)">
        <i class="bi bi-check-all"></i> Select All
      </BButton>
      <BButton v-if="selectedColumns.length > 0" size="sm" variant="outline-primary" :disabled="!canMoveLeft" @click="reorderColumns('left')" title="Move selected columns one step left">
        <i class="bi bi-arrow-left"></i>
      </BButton>
      <BButton v-if="selectedColumns.length > 0" size="sm" variant="outline-primary" :disabled="!canMoveRight" @click="reorderColumns('right')" title="Move selected columns one step right">
        <i class="bi bi-arrow-right"></i>
      </BButton>
      <BButton size="sm" variant="outline-primary" @click="showColumnReorderModal = true" title="Open column reorder dialog">
        <i class="bi bi-arrow-left-right"></i>
      </BButton>
      <BButton v-if="rowSelectMode && selectedRowIndices.length > 0" size="sm" variant="outline-primary" :disabled="!canMoveRowUp" @click="reorderRows('up')" title="Move selected rows one step up">
        <i class="bi bi-arrow-up"></i>
      </BButton>
      <BButton v-if="rowSelectMode && selectedRowIndices.length > 0" size="sm" variant="outline-primary" :disabled="!canMoveRowDown" @click="reorderRows('down')" title="Move selected rows one step down">
        <i class="bi bi-arrow-down"></i>
      </BButton>
      <BButton size="sm" variant="primary" @click="showAddRecords = true">
        <i class="bi bi-plus-lg me-1"></i>Add
      </BButton>
      <BButton v-if="rowSelectMode && selectedRowIndices.length > 0" size="sm" variant="outline-danger" @click="deleteSelectedRows">
        <i class="bi bi-trash me-1"></i>Delete {{ selectedRowIndices.length }}
      </BButton>
       <!-- Column visibility dropdown -->
       <BDropdown size="sm" variant="outline-secondary" class="column-visibility-dropdown" no-caret>
         <template #button-content>
           <i class="bi bi-eye"></i>
           <span v-if="hiddenColumns.length > 0" class="badge bg-warning ms-1" style="font-size: 0.6rem;">{{ hiddenColumns.length }}</span>
         </template>
         <BDropdownItemButton
           v-for="field in columns"
           :key="field.field"
           :class="{ 'text-muted': hiddenColumns.includes(field.field) }"
           @click.stop="toggleVisibility(field.field)"
         >
           <i :class="hiddenColumns.includes(field.field) ? 'bi bi-eye-slash' : 'bi bi-eye'" class="me-1"></i>
           {{ field.label }}
         </BDropdownItemButton>
         <BDropdownDivider v-if="hiddenColumns.length > 0" />
         <BDropdownItemButton v-if="hiddenColumns.length > 0" @click="unhideAllColumns">
           <i class="bi bi-eye-fill me-1"></i> Show All
         </BDropdownItemButton>
       </BDropdown>
      <BButton size="sm" :variant="'outline-secondary'" @click="showTableSettings = true">
        <i class="bi bi-gear"></i>
      </BButton>      
      <span v-if="selectedColumns.length === 0" class="text-muted small ms-2">
        <i class="bi bi-info-circle me-1"></i>Click column headers to select
      </span>
      <!-- Row Scope Selector -->
      <div v-if="rowSelectMode && selectedRowIndices.length" class="d-flex align-items-center gap-1 ms-2" title="Apply operations to selected rows only">
        <small class="text-muted">Scope:</small>
        <BFormSelect 
          v-model="operationRowScope" 
          size="sm" 
          :options="[
            { value: 'all', text: 'All rows' },
            { value: 'selected', text: 'Selected (' + selectedRowIndices.length + ')' }
          ]"
          :disabled="operationRowScope === 'selected' && selectedRowIndices.length === 0"
          style="width: auto; min-width: 120px;"
        ></BFormSelect>
      </div>      
      <!-- Apply to Hidden Columns Toggle -->
      <div v-if="hiddenColumns.length > 0" class="d-flex align-items-center gap-1 ms-2" title="Include hidden columns in operations">
        <input class="form-check-input m-0" type="checkbox" v-model="applyToHiddenColumns" id="apply-to-hidden">
        <label class="form-check-label small text-muted cursor-pointer" for="apply-to-hidden">Apply to hidden</label>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Data Table -->
    <div v-else class="card">
      <!-- Custom DataTable (no pagination - handled below) -->
      <DataTable
        ref="dataTableRef"
        :items="filteredData"
        :fields="tableFields"
        :selected-columns="selectedColumns"
        :selectable="rowSelectMode"
        :selected-rows="selectedRowIndices"
        :show-index="showRowIndex"
        :multi-sort="multiSort"
        :server-sort="sortKeys"
        :show-footer="showFooter"
        :footer-stats="footerStats"
        :enable-column-filter="enableColumnFilter"
        :column-unique-values="columnUniqueValues"
        :column-filter-state="columnFilterState"
        :fetching-unique-values="fetchingUniqueValues"
        :column-unique-counts="columnUniqueCounts"
        :hidden-columns="hiddenColumns"
        @row-clicked="onRowClicked"
        @head-clicked="onHeadClicked"
        @row-selected="toggleRowSelection"
        @toggle-all="toggleAllRows"
        @cell-dblclick="openCellEditor"
        @hidden-columns-changed="onHiddenColumnsChanged"
        @column-filter-changed="onColumnFilterChanged"
        @request-unique-values="fetchUniqueValuesForColumn"
        @sort-changed="onSortChanged"
      />

      <!-- Pagination Footer -->
      <div class="d-flex justify-content-between align-items-center m-2 flex-wrap gap-2">
        <small class="text-muted">
          Showing {{ startRow }} - {{ endRow }} of {{ totalRows }}
        </small>
        <div class="d-flex align-items-center gap-1 flex-wrap">
          <!-- First Page Button -->
          <BButton
            variant="outline-secondary"
            size="sm"
            :disabled="page <= 1"
            @click="goToPage(1)"
            title="First page"
          >
            <i class="bi bi-chevron-double-left"></i>
          </BButton>
          <!-- Previous Page Button -->
          <BButton
            variant="outline-secondary"
            size="sm"
            :disabled="page <= 1"
            @click="goToPrev"
            title="Previous page"
          >
            <i class="bi bi-chevron-left"></i>
          </BButton>
          
          <!-- Page Numbers -->
          <template v-for="p in pageNumbers" :key="p">
            <span v-if="p === '...'" class="px-1 text-muted">…</span>
            <BButton
              v-else
              :variant="p === page ? 'primary' : 'outline-secondary'"
              size="sm"
              @click="goToPage(p)"
            >
              {{ p }}
            </BButton>
          </template>
          
          <!-- Next Page Button -->
          <BButton
            variant="outline-secondary"
            size="sm"
            :disabled="page >= totalPages"
            @click="goToNext"
            title="Next page"
          >
            <i class="bi bi-chevron-right"></i>
          </BButton>
          <!-- Last Page Button -->
          <BButton
            variant="outline-secondary"
            size="sm"
            :disabled="page >= totalPages"
            @click="goToPage(totalPages)"
            title="Last page"
          >
            <i class="bi bi-chevron-double-right"></i>
          </BButton>
          
          <!-- Jump to Page -->
          <div class="d-flex align-items-center gap-1 ms-2">
            <small class="text-muted">Go to</small>
            <BFormInput
              v-model.number="jumpToPage"
              type="number"
              min="1"
              :max="totalPages"
              size="sm"
              style="width: 70px;"
              @keyup.enter="goToPage(jumpToPage)"
              placeholder="Page"
            />
            <BButton
              variant="outline-primary"
              size="sm"
              :disabled="!jumpToPage || jumpToPage < 1 || jumpToPage > totalPages"
              @click="goToPage(jumpToPage)"
            >
              Go
            </BButton>
          </div>

        </div>
      </div>
    </div>

    <!-- Profile Modal -->
    <ProfileModal
      v-model="showProfile"
      :profile-data="profileData"
    />



    <!-- Clipboard Import Modal -->
    <BModal v-model="showClipboardImport" title="Import from Clipboard">
      <BFormGroup label="Dataset Name">
        <BFormInput v-model="clipboardDatasetName" placeholder="My Dataset"></BFormInput>
      </BFormGroup>
      <BFormGroup label="CSV Data">
        <template #label>
          <div class="d-flex justify-content-between align-items-center">
            <span>CSV Data</span>
            <BButton size="sm" @click="pasteFromClipboard">
              <i class="bi bi-clipboard me-1"></i> Paste from Clipboard
            </BButton>
          </div>
        </template>
        <BFormTextarea v-model="clipboardData" :rows="10" placeholder="Paste your CSV data here..."></BFormTextarea>
      </BFormGroup>
      <template #footer>
        <BButton @click="showClipboardImport = false">Cancel</BButton>
        <BButton variant="primary" :loading="operating" @click="importFromClipboard">Import</BButton>
      </template>
    </BModal>

    <!-- Fill NA Modal -->
    <BModal v-model="showFillnaModal" title="Fill Missing Values">
      <BFormGroup label="Fill Value">
        <BFormInput v-model="fillValue" placeholder="Enter value to fill"></BFormInput>
      </BFormGroup>
      <template #footer>
        <BButton @click="showFillnaModal = false">Cancel</BButton>
        <BButton variant="primary" :loading="operating" @click="applyOperation('fillna', { method: 'constant', fill_value: fillValue })">Apply</BButton>
      </template>
    </BModal>

    <!-- Extract JSON Modal -->
    <BModal v-model="showExtractJsonModal" title="Extract JSON Value" size="lg">
      <div class="alert alert-info py-2 mb-3">
        <i class="bi bi-info-circle me-1"></i>
        Extract a value from JSON strings in <strong>{{ selectedColumns[0] || 'selected column' }}</strong>.
        Non-JSON values are left unchanged.
      </div>
      <div v-if="extractJsonSamples.length" class="mb-3">
        <label class="form-label fw-bold small">Sample values:</label>
        <div class="bg-light p-2 rounded" style="max-height: 120px; overflow-y: auto;">
          <code v-for="(s, i) in extractJsonSamples" :key="i" class="d-block small text-truncate mb-1">{{ s }}</code>
        </div>
      </div>
      <div v-if="extractJsonSuggestedKeys.length" class="mb-3">
        <label class="form-label fw-bold small">Detected keys:</label>
        <div class="d-flex flex-wrap gap-1">
          <button
            v-for="k in extractJsonSuggestedKeys"
            :key="k"
            class="btn btn-sm"
            :class="extractJsonKey === k ? 'btn-primary' : 'btn-outline-secondary'"
            @click="extractJsonKey = k"
          >{{ k }}</button>
        </div>
      </div>
      <BFormGroup label="Key to extract (dot notation for nested: a.b)">
        <BFormInput v-model="extractJsonKey" placeholder="e.g., country, data.value"></BFormInput>
      </BFormGroup>
      <template #footer>
        <BButton @click="showExtractJsonModal = false">Cancel</BButton>
        <BButton variant="primary" :loading="operating" :disabled="!extractJsonKey" @click="applyExtractJson">Extract</BButton>
      </template>
    </BModal>

  <!-- Extract Pattern Modal -->
  <ExtractPatternModal
    v-model="showExtractPatternModal"
    :column="selectedColumns[0] || ''"
    :samples="extractPatternSamples"
    :dataset-id="datasetId"
    :loading="operating"
    :agent-options="agentOptions"
    @apply="applyExtractPattern"
  />

  <!-- Find & Replace Modal -->
  <BModal v-model="showFindReplaceModal" title="Find & Replace">
      <div class="alert alert-info py-2 mb-3">
        <i class="bi bi-info-circle me-1"></i>
        Replace values in <strong>{{ selectedColumns.length ? selectedColumns.join(', ') : 'selected column(s)' }}</strong>.
      </div>
      <BFormGroup label="Find" label-for="find-input">
        <BFormInput id="find-input" v-model="findValue" placeholder="Text or regex to find"></BFormInput>
      </BFormGroup>
      <BFormGroup label="Replace with" label-for="replace-input">
        <BFormInput id="replace-input" v-model="replaceValue" placeholder="Replacement text"></BFormInput>
      </BFormGroup>
      <div class="form-check mb-2">
        <input class="form-check-input" type="checkbox" v-model="findReplaceRegex" id="fr-regex">
        <label class="form-check-label" for="fr-regex">Use regex</label>
      </div>
      <div class="form-check">
        <input class="form-check-input" type="checkbox" v-model="findReplaceCaseSensitive" id="fr-case">
        <label class="form-check-label" for="fr-case">Case sensitive</label>
      </div>
      <template #footer>
        <BButton @click="showFindReplaceModal = false">Cancel</BButton>
        <BButton variant="primary" :loading="operating" :disabled="!findValue" @click="applyFindReplace">Replace</BButton>
      </template>
    </BModal>

    <!-- Structural AI Clean Modal -->
    <AiCleanModal
      v-model="showStructuralAiModal"
      type="structural"
      :selected-columns="selectedColumns"
      :agent-options="agentOptions"
      :total-rows="totalRows"
      :operating="operating"
      @apply="applyStructuralAiClean"
    />

    <!-- Data AI Clean Modal -->
    <AiCleanModal
      v-model="showDataAiModal"
      type="data"
      :selected-columns="selectedColumns"
      :agent-options="agentOptions"
      :total-rows="totalRows"
      :operating="operating"
      :batch-progress="batchProgress"
      :fuzzy-context="fuzzyAiContext"
      @apply="applyDataAiClean"
      @close="closeDataAiModal"
    />

    <!-- Fuzzy Match Modal -->
    <FuzzyMatchModal
      v-model="showFuzzyMatchModal"
      :columns="columns"
      :dataset-id="datasetId"
      :agent-options="agentOptions"
      :selected-columns="selectedColumns"
      @apply="onFuzzyMatchApply"
      @aiHelp="onFuzzyAiHelp"
    />

    <!-- Operation Confirm Modal -->
    <OperationConfirmModal
      v-model="showOpConfirm"
      :title="opConfirmConfig.title"
      :description="opConfirmConfig.description"
      :options="opConfirmConfig.options"
      :defaults="opConfirmConfig.params"
      :selected-columns="selectedColumns"
      :loading="operating"
      @apply="onOpConfirmApply"
    />

    <!-- Clone Column Modal -->
    <BModal v-model="showCloneModal" title="Clone Column" size="sm">
      <div class="alert alert-info py-2 small mb-3">
        <i class="bi bi-info-circle me-1"></i>
        Create a copy of <strong>{{ selectedColumns[0] }}</strong> with a new name. Useful before applying transformations to preserve the original.
      </div>
      <BFormGroup label="New column name" label-size="sm">
        <BFormInput v-model="cloneNewName" size="sm" :placeholder="selectedColumns[0] + '_copy'"></BFormInput>
      </BFormGroup>
      <template #footer>
        <BButton variant="outline-secondary" @click="showCloneModal = false">Cancel</BButton>
        <BButton variant="primary" :loading="operating" :disabled="!cloneNewName" @click="applyCloneColumn">
          <i class="bi bi-copy me-1"></i>Clone
        </BButton>
      </template>
    </BModal>

    <!-- Merge Columns Modal -->
    <BModal v-model="showMergeModal" title="Merge Columns" size="md">
      <div class="alert alert-info py-2 small mb-3">
        <i class="bi bi-info-circle me-1"></i>
        Combine values from multiple columns into a single new column using a delimiter.
      </div>
      <BFormGroup label="Select columns to merge" label-size="sm">
        <div class="d-flex flex-wrap gap-2">
          <div v-for="col in columns" :key="col.field" class="form-check">
            <input class="form-check-input" type="checkbox" :value="col.field" v-model="mergeColumns" :id="'merge-' + col.field">
            <label class="form-check-label small" :for="'merge-' + col.field">{{ col.label || col.field }}</label>
          </div>
        </div>
      </BFormGroup>
      <BFormGroup label="New column name" label-size="sm" class="mt-2">
        <BFormInput v-model="mergeNewColumn" size="sm" placeholder="e.g. full_name"></BFormInput>
      </BFormGroup>
      <BFormGroup label="Delimiter" label-size="sm" class="mt-2">
        <BFormInput v-model="mergeDelimiter" size="sm" placeholder="e.g. space, comma, dash"></BFormInput>
        <small class="text-muted">Character(s) between merged values. Leave empty for concatenation.</small>
      </BFormGroup>
      <div v-if="mergeColumns.length >= 2" class="mt-2 p-2 bg-light rounded small">
        <strong>Preview:</strong> {{ mergeColumns.map(c => data[0]?.[c] ?? '…').join(mergeDelimiter || '') }}
      </div>
      <template #footer>
        <BButton variant="outline-secondary" @click="showMergeModal = false">Cancel</BButton>
        <BButton variant="primary" :loading="operating" :disabled="mergeColumns.length < 2 || !mergeNewColumn" @click="applyMerge">
          <i class="bi bi-arrows-collapse me-1"></i>Merge
        </BButton>
      </template>
    </BModal>

    <!-- Split Column Modal -->
    <BModal v-model="showSplitModal" title="Split Column" size="md">
      <div class="alert alert-info py-2 small mb-3">
        <i class="bi bi-info-circle me-1"></i>
        Split <strong>{{ selectedColumns[0] || 'selected column' }}</strong> into multiple columns using a delimiter.
      </div>
      <BFormGroup label="Delimiter" label-size="sm">
        <BFormInput v-model="splitDelimiter" size="sm" placeholder="e.g. space, comma, -"></BFormInput>
        <small class="text-muted">Character(s) to split on.</small>
      </BFormGroup>
      <BFormGroup label="New column names" label-size="sm" class="mt-2">
        <div class="d-flex gap-2 align-items-center mb-2">
          <BFormInput v-model="splitNewColName" size="sm" placeholder="Column name" style="max-width: 200px;"></BFormInput>
          <BButton size="sm" variant="outline-primary" @click="addSplitColumn" :disabled="!splitNewColName">
            <i class="bi bi-plus"></i>
          </BButton>
        </div>
        <div class="d-flex flex-wrap gap-1">
          <span v-for="(name, i) in splitNewColumns" :key="i" class="badge bg-light text-dark d-flex align-items-center gap-1">
            {{ name }}
            <button class="btn-close btn-close-sm" style="font-size: 0.6rem;" @click="splitNewColumns.splice(i, 1)"></button>
          </span>
        </div>
      </BFormGroup>
      <div v-if="splitDelimiter && selectedColumns.length === 1" class="mt-2 p-2 bg-light rounded small">
        <strong>Preview:</strong> {{ (data[0]?.[selectedColumns[0]] || '').toString().split(splitDelimiter).join(' | ') }}
      </div>
      <template #footer>
        <BButton variant="outline-secondary" @click="showSplitModal = false">Cancel</BButton>
        <BButton variant="primary" :loading="operating" :disabled="!splitDelimiter || splitNewColumns.length < 2" @click="applySplit">
          <i class="bi bi-arrows-expand me-1"></i>Split
        </BButton>
      </template>
    </BModal>

    <!-- ML Encoding Modal -->
    <BModal v-model="showEncodingModal" :title="encodingConfig.title" size="md" no-close-on-backdrop>
      <div class="alert alert-info py-2 small mb-3">
        <i class="bi bi-info-circle me-1"></i>{{ encodingConfig.description }}
      </div>
      <div class="mb-2 small text-muted">
        Column: <strong>{{ selectedColumns[0] || 'none selected' }}</strong>
      </div>

      <!-- One-Hot options -->
      <div v-if="encodingOp === 'one_hot'">
        <BFormGroup label="Column prefix" label-size="sm">
          <BFormInput v-model="encodingParams.prefix" size="sm" :placeholder="selectedColumns[0] || 'prefix'"></BFormInput>
        </BFormGroup>
        <div v-if="encodingPreview.length" class="mt-2 p-2 bg-light rounded small">
          <strong>Preview (first row):</strong>
          <div v-for="(val, key) in encodingPreview[0]" :key="key" class="d-flex gap-2">
            <span class="text-muted">{{ key }}:</span> <span>{{ val }}</span>
          </div>
        </div>
      </div>

      <!-- Label options -->
      <div v-if="encodingOp === 'label'">
        <div v-if="encodingPreview.length" class="mt-2 p-2 bg-light rounded small">
          <strong>Category mapping:</strong>
          <div v-for="item in encodingPreview" :key="item.value" class="d-flex gap-2">
            <span class="badge bg-light text-dark">{{ item.value }}</span> → <span class="badge bg-primary">{{ item.label }}</span>
          </div>
        </div>
      </div>

      <!-- Map options -->
      <div v-if="encodingOp === 'map'">
        <BFormGroup label="Mapping (JSON object)" label-size="sm">
          <BFormTextarea v-model="encodingParams.mappingJson" rows="4" size="sm" placeholder='{"Y": "Yes", "N": "No"}'></BFormTextarea>
        </BFormGroup>
        <small class="text-muted">Enter a JSON object: {"original": "new", ...}</small>
      </div>

      <!-- Binning options -->
      <div v-if="encodingOp === 'bin'">
        <BFormGroup label="Number of bins" label-size="sm">
          <BFormInput v-model.number="encodingParams.n_bins" type="number" min="2" max="20" size="sm"></BFormInput>
        </BFormGroup>
        <BFormGroup label="Strategy" label-size="sm" class="mt-2">
          <BFormSelect v-model="encodingParams.strategy" size="sm" :options="[
            { value: 'equal_width', text: 'Equal width (uniform intervals)' },
            { value: 'equal_freq', text: 'Equal frequency (same count per bin)' },
          ]"></BFormSelect>
        </BFormGroup>
        <div v-if="encodingPreview.length" class="mt-2 p-2 bg-light rounded small">
          <strong>Preview (first rows):</strong>
          <div v-for="(item, i) in encodingPreview.slice(0, 5)" :key="i" class="d-flex gap-2">
            <span>{{ item.original }}</span> → <span class="badge bg-primary">{{ item.binned }}</span>
          </div>
        </div>
      </div>

      <template #footer>
        <BButton variant="outline-secondary" @click="showEncodingModal = false">Cancel</BButton>
        <BButton variant="primary" :loading="operating" :disabled="!selectedColumns.length" @click="applyEncoding">
          <i class="bi bi-play-fill me-1"></i>Apply
        </BButton>
      </template>
    </BModal>

    <!-- Cell Edit Modal -->
    <BModal v-model="showCellEdit" :title="'Edit Cell — ' + cellEdit.column" size="sm">
      <div class="small text-muted mb-2">
        Row {{ cellEdit.row + 1 }}, Column <strong>{{ cellEdit.column }}</strong>
      </div>
      <BFormTextarea v-model="cellEdit.value" rows="3" autofocus></BFormTextarea>
      <template #footer>
        <BButton variant="outline-secondary" @click="showCellEdit = false">Cancel</BButton>
        <BButton variant="primary" :loading="operating" @click="saveCellEdit">
          <i class="bi bi-check-lg me-1"></i>Save
        </BButton>
      </template>
    </BModal>

    <!-- Table Settings Modal -->
    <BModal v-model="showTableSettings" title="Table Settings" size="sm">
      <div class="d-flex flex-column gap-3">
        <div class="form-check form-switch">
          <input class="form-check-input" type="checkbox" v-model="showRowIndex" id="setting-index">
          <label class="form-check-label" for="setting-index">
            <strong>Show row index</strong>
            <small class="d-block text-muted">Display sequential numbers (1, 2, 3…) in the first column</small>
          </label>
        </div>
        <div class="form-check form-switch">
          <input class="form-check-input" type="checkbox" v-model="rowSelectMode" id="setting-select" @change="onRowSelectToggle">
          <label class="form-check-label" for="setting-select">
            <strong>Row selection mode</strong>
            <small class="d-block text-muted">Enable checkboxes to select and reorder rows</small>
          </label>
        </div>
        <div class="form-check form-switch">
          <input class="form-check-input" type="checkbox" v-model="multiSort" id="setting-multisort">
          <label class="form-check-label" for="setting-multisort">
            <strong>Multi-column sorting</strong>
            <small class="d-block text-muted">Sort by multiple columns by clicking headers sequentially</small>
          </label>
        </div>

        <div class="form-check form-switch">
          <input class="form-check-input" type="checkbox" v-model="enableColumnFilter" id="setting-column-filter">
          <label class="form-check-label" for="setting-column-filter">
            <strong>Multi-column filtering</strong>
            <small class="d-block text-muted">Show filter dropdowns on column headers to filter by selected values</small>
          </label>
        </div>

        <div class="form-check form-switch">
          <input class="form-check-input" type="checkbox" v-model="showFooter" id="setting-footer" @change="onShowFooterToggle">
          <label class="form-check-label" for="setting-footer">
            <strong>Stats footer</strong>
            <small class="d-block text-muted">Show summary statistics at bottom of each page</small>
          </label>
        </div>

        </div>
      <template #footer>
        <BButton variant="primary" size="sm" @click="showTableSettings = false">Done</BButton>
      </template>
    </BModal>

    <!-- Export Recipe Modal -->
    <BModal v-model="showExportRecipe" title="Export Operations Recipe" size="md">
      <p class="text-muted small mb-3">Export completed operations as a JSON recipe that can be imported into another dataset.</p>
      <div class="mb-3">
        <strong class="small">{{ completedOpsCount }} operation(s)</strong> will be exported.
      </div>
      <div class="form-check mb-3">
        <input class="form-check-input" type="checkbox" v-model="exportZip" id="export-zip">
        <label class="form-check-label" for="export-zip">
          <i class="bi bi-file-zip me-1"></i>Download as ZIP <small class="text-muted">(for large histories)</small>
        </label>
      </div>
      <template #footer>
        <BButton variant="outline-secondary" @click="showExportRecipe = false">Cancel</BButton>
        <BButton variant="success" :disabled="completedOpsCount === 0" @click="exportOperations">
          <i class="bi bi-download me-1"></i>Export
        </BButton>
      </template>
    </BModal>

    <!-- Import Recipe Modal -->
    <BModal v-model="showImportRecipe" title="Import Operations Recipe" size="lg" no-close-on-backdrop>
      <!-- Step 1: Input -->
      <div v-if="!importPreview && !importResults">
        <ul class="nav nav-pills mb-3">
          <li class="nav-item">
            <button class="nav-link" :class="{ active: importMode === 'paste' }" @click="importMode = 'paste'">
              <i class="bi bi-clipboard me-1"></i> Paste JSON
            </button>
          </li>
          <li class="nav-item">
            <button class="nav-link" :class="{ active: importMode === 'file' }" @click="importMode = 'file'">
              <i class="bi bi-file-earmark-arrow-up me-1"></i> Upload File
            </button>
          </li>
        </ul>

        <div v-if="importMode === 'paste'">
          <BFormTextarea v-model="importText" rows="8" placeholder='[{"operation": "fillna", "column": "email", "params": {"method": "constant", "fill_value": "N/A"}}]'></BFormTextarea>
          <div v-if="importError" class="alert alert-danger py-2 mt-2 small">{{ importError }}</div>
        </div>

        <div v-if="importMode === 'file'">
          <BFormFile v-model="importFile" accept=".json,.zip" @update:model-value="onImportFileSelected"></BFormFile>
          <div v-if="importError" class="alert alert-danger py-2 mt-2 small">{{ importError }}</div>
        </div>
      </div>

      <!-- Step 2: Preview -->
      <div v-if="importPreview">
        <div class="alert alert-info py-2 small mb-3">
          <i class="bi bi-info-circle me-1"></i>
          Review operations before applying.
        </div>
        <div class="d-flex align-items-center gap-2 mb-2">
          <input class="form-check-input" type="checkbox" :checked="allImportSelected" :indeterminate="someImportSelected && !allImportSelected" @change="toggleAllImport">
          <label class="form-check-label small fw-bold">Select all</label>
          <span class="text-muted small ms-auto">{{ importPreview.filter(o => o.selected).length }}/{{ importPreview.length }} selected</span>
        </div>
        <div v-for="(op, i) in importPreview" :key="i" class="d-flex align-items-start gap-2 mb-2 p-2 rounded" :class="op.column_missing ? 'bg-warning bg-opacity-10' : 'bg-light'">
          <input class="form-check-input mt-1" type="checkbox" v-model="op.selected" :disabled="op.column_missing">
          <div class="flex-grow-1">
            <div class="d-flex align-items-center gap-1">
              <span class="badge" :class="op.column_missing ? 'bg-warning' : 'bg-primary'">{{ op.operation }}</span>
              <small v-if="op.column" class="text-muted">{{ op.column }}</small>
              <small v-if="op.columns" class="text-muted">{{ op.columns?.join(', ') }}</small>
            </div>
            <small class="text-muted d-block">{{ formatOpParamsPretty(op.params) }}</small>
            <small v-if="op.column_missing" class="text-warning d-block">
              <i class="bi bi-exclamation-triangle me-1"></i>Column(s) not found — will be skipped
            </small>
          </div>
        </div>
      </div>

      <!-- Step 3: Results -->
      <div v-if="importResults">
        <div class="alert" :class="importResults.status === 'success' ? 'alert-success' : importResults.status === 'partial' ? 'alert-warning' : 'alert-danger'" py-2>
          <i class="bi me-1" :class="importResults.status === 'success' ? 'bi-check-circle' : 'bi-exclamation-triangle'"></i>
          <strong>{{ importResults.message }}</strong>
        </div>
        <div v-for="(r, i) in importResults.results" :key="i" class="d-flex align-items-center gap-2 mb-1 small">
          <i class="bi" :class="r.status === 'success' ? 'bi-check-circle text-success' : r.status === 'skipped' ? 'bi-skip-circle text-warning' : 'bi-x-circle text-danger'"></i>
          <span class="badge bg-light text-dark">{{ r.operation }}</span>
          <span v-if="r.column" class="text-muted">{{ r.column }}</span>
          <span class="text-muted">{{ r.message }}</span>
        </div>
      </div>

      <template #footer>
        <BButton v-if="importResults" variant="primary" @click="closeImportModal">Done</BButton>
        <template v-else-if="importPreview">
          <BButton variant="outline-secondary" @click="importPreview = null">Back</BButton>
          <BButton variant="primary" :loading="operating" :disabled="!importPreview.some(o => o.selected)" @click="applyImportedRecipe">
            <i class="bi bi-play me-1"></i>Apply {{ importPreview.filter(o => o.selected).length }} Operation(s)
          </BButton>
        </template>
        <template v-else>
          <BButton variant="outline-secondary" @click="showImportRecipe = false">Cancel</BButton>
          <BButton variant="primary" :disabled="!canParseImport" @click="parseImport">
            <i class="bi bi-arrow-right me-1"></i>Next: Preview
          </BButton>
        </template>
      </template>
    </BModal>

    <!-- Add Records Modal -->
    <BModal v-model="showAddRecords" title="Add Records" size="lg">
      <ul class="nav nav-pills mb-3">
        <li class="nav-item">
          <button class="nav-link" :class="{ active: addMode === 'single' }" @click="addMode = 'single'">
            <i class="bi bi-plus-circle me-1"></i> Single Row
          </button>
        </li>
        <li class="nav-item">
          <button class="nav-link" :class="{ active: addMode === 'csv' }" @click="addMode = 'csv'">
            <i class="bi bi-file-earmark-text me-1"></i> Paste CSV
          </button>
        </li>
        <li class="nav-item">
          <button class="nav-link" :class="{ active: addMode === 'json' }" @click="addMode = 'json'">
            <i class="bi bi-braces me-1"></i> Paste JSON
          </button>
        </li>
      </ul>

      <!-- Single Row Mode -->
      <div v-if="addMode === 'single'">
        <div class="row g-2">
          <div v-for="col in columns" :key="col.field" class="col-md-6">
            <BFormGroup :label="col.label || col.field" :label-for="'add-' + col.field" label-size="sm">
              <BFormInput :id="'add-' + col.field" v-model="singleRow[col.field]" size="sm" :placeholder="'Enter ' + (col.label || col.field)"></BFormInput>
            </BFormGroup>
          </div>
        </div>
        <div class="mt-2">
          <BButton size="sm" variant="outline-secondary" @click="addAnotherRow">
            <i class="bi bi-plus me-1"></i>Add another row
          </BButton>
          <span v-if="pendingRows.length" class="ms-2 text-muted small">{{ pendingRows.length }} row(s) ready</span>
        </div>
      </div>

      <!-- CSV Mode -->
      <div v-if="addMode === 'csv'">
        <div class="alert alert-info py-2 small mb-2">
          <i class="bi bi-info-circle me-1"></i>
          Paste CSV data with headers matching the dataset columns: <strong>{{ columns.map(c => c.field).join(', ') }}</strong>
        </div>
        <BFormTextarea v-model="csvText" rows="8" placeholder="name,age,city&#10;Alice,30,Paris&#10;Bob,25,London"></BFormTextarea>
      </div>

      <!-- JSON Mode -->
      <div v-if="addMode === 'json'">
        <div class="alert alert-info py-2 small mb-2">
          <i class="bi bi-info-circle me-1"></i>
          Paste a JSON array of objects. Keys should match dataset columns: <strong>{{ columns.map(c => c.field).join(', ') }}</strong>
        </div>
        <BFormTextarea v-model="jsonText" rows="8" placeholder='[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]'></BFormTextarea>
      </div>

      <template #footer>
        <BButton variant="outline-secondary" @click="showAddRecords = false">Cancel</BButton>
        <BButton variant="primary" :loading="operating" :disabled="!canAddRecords" @click="submitAddRecords">
          <i class="bi bi-plus-lg me-1"></i>Add Records
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

    <!-- Row Filter Modal -->
    <BModal v-model="showRowFilterModal" title="Filter Rows" size="lg">
      <div class="alert alert-secondary mb-3">
        <i class="bi bi-info-circle me-1"></i>
        <strong>Multi-column filter:</strong> Enter a value for any column to filter. Only rows matching <em>all</em> criteria are shown.
        Leave fields empty to skip that column. Filtered rows can be deleted via the "Rows → Delete visible" menu.
        Other operations (rename, sort, AI clean) still apply to the <strong>full dataset</strong>.
      </div>
      <div v-if="hasActiveFilter" class="alert alert-warning py-2 mb-3">
        <i class="bi bi-funnel-fill me-1"></i>
        Showing {{ filteredData.length }} of {{ data.length }} rows matching current filter.
      </div>
      <div class="row g-2">
        <div v-for="col in columns" :key="col.field" class="col-md-6">
          <BFormGroup :label="col.label || col.field" :label-for="'filter-' + col.field" label-size="sm">
            <BFormInput
              :id="'filter-' + col.field"
              v-model="rowFilters[col.field]"
              size="sm"
              :placeholder="'Filter ' + (col.label || col.field) + '...'"
            ></BFormInput>
          </BFormGroup>
        </div>
      </div>
      <template #footer>
        <BButton variant="outline-secondary" @click="clearRowFilter">Clear all</BButton>
        <BButton @click="showRowFilterModal = false">Cancel</BButton>
        <BButton variant="primary" @click="applyRowFilter">Apply filter</BButton>
      </template>
    </BModal>

    <!-- Compare Modal -->
    <BModal v-model="showCompare" title="Compare Operations" size="lg">
      <p class="text-muted">Compare data before and after a cleaning operation.</p>
      
      <BFormGroup label="Select Operation" class="mb-3">
        <BFormSelect v-model="compareOpId" :options="operationOptions"></BFormSelect>
      </BFormGroup>

      <!-- Comparison Results -->
      <div v-if="comparisonResult" class="comparison-results">
        <!-- Summary Cards -->
        <div class="row g-2 mb-3">
          <div class="col-6 col-md-3">
            <div class="card text-center">
              <div class="card-body py-2">
                <h4 class="mb-0 text-success">{{ comparisonResult.changes_summary?.columns_added?.length || 0 }}</h4>
                <small class="text-muted">Columns Added</small>
              </div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="card text-center">
              <div class="card-body py-2">
                <h4 class="mb-0 text-danger">{{ comparisonResult.changes_summary?.columns_removed?.length || 0 }}</h4>
                <small class="text-muted">Columns Removed</small>
              </div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="card text-center">
              <div class="card-body py-2">
                <h4 class="mb-0 text-warning">{{ comparisonResult.changes_summary?.columns_renamed?.length || 0 }}</h4>
                <small class="text-muted">Columns Changed</small>
              </div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="card text-center">
              <div class="card-body py-2">
                <h4 class="mb-0" :class="comparisonResult.changes_summary?.rows_changed > 0 ? 'text-success' : comparisonResult.changes_summary?.rows_changed < 0 ? 'text-danger' : ''">
                  {{ comparisonResult.changes_summary?.rows_changed || 0 }}
                </h4>
                <small class="text-muted">Rows Changed</small>
              </div>
            </div>
          </div>
        </div>

        <!-- Columns Added -->
        <div v-if="comparisonResult.changes_summary?.columns_added?.length" class="mb-3">
          <h6 class="text-success"><i class="bi bi-plus-circle me-1"></i>Columns Added</h6>
          <div class="d-flex flex-wrap gap-1">
            <BBadge v-for="col in comparisonResult.changes_summary.columns_added" :key="col" variant="success">
              {{ col }}
            </BBadge>
          </div>
        </div>

        <!-- Columns Removed -->
        <div v-if="comparisonResult.changes_summary?.columns_removed?.length" class="mb-3">
          <h6 class="text-danger"><i class="bi bi-dash-circle me-1"></i>Columns Removed</h6>
          <div class="d-flex flex-wrap gap-1">
            <BBadge v-for="col in comparisonResult.changes_summary.columns_removed" :key="col" variant="danger">
              {{ col }}
            </BBadge>
          </div>
        </div>

        <!-- Columns Changed -->
        <div v-if="comparisonResult.changes_summary?.columns_renamed?.length" class="mb-3">
          <h6 class="text-warning"><i class="bi bi-pencil me-1"></i>Columns Changed</h6>
          <div class="d-flex flex-wrap gap-1">
            <BBadge v-for="col in comparisonResult.changes_summary.columns_renamed" :key="col.from" variant="warning">
              {{ col.from }} → {{ col.to }}
            </BBadge>
          </div>
        </div>

        <!-- Column Details -->
        <div class="row">
          <div class="col-6">
            <h6>Before ({{ comparisonResult.before_columns?.length || 0 }} columns)</h6>
            <ul class="list-group" style="max-height: 200px; overflow-y: auto;">
              <li v-for="col in comparisonResult.before_columns" :key="col.name" class="list-group-item py-1 small">
                {{ col.name }}
              </li>
            </ul>
          </div>
          <div class="col-6">
            <h6>After ({{ comparisonResult.after_columns?.length || 0 }} columns)</h6>
            <ul class="list-group" style="max-height: 200px; overflow-y: auto;">
              <li v-for="col in comparisonResult.after_columns" :key="col.name" class="list-group-item py-1 small">
                {{ col.name }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div v-else-if="comparing" class="text-center py-4">
        <div class="spinner-border text-primary"></div>
        <p class="mt-2 text-muted">Loading comparison...</p>
      </div>

      <div v-else class="text-center py-4 text-muted">
        <i class="bi bi-arrow-left-right fs-1"></i>
        <p>Select an operation and click Compare</p>
      </div>

      <template #footer>
        <BButton @click="showCompare = false">Close</BButton>
        <BButton variant="primary" :loading="comparing" :disabled="!compareOpId" @click="loadComparison">
          Compare
        </BButton>
      </template>
    </BModal>

    <!-- Reusable Prompt Modal -->
    <PromptModal
      v-model="promptConfig.show"
      :title="promptConfig.title"
      :message="promptConfig.message"
      :default-value="promptConfig.defaultValue"
      :input-type="promptConfig.inputType"
      :confirm-text="promptConfig.confirmText"
      @confirm="onPromptConfirm"
      @cancel="onPromptCancel"
    />

    <!-- Reusable Confirm Modal -->
    <BModal v-model="confirmConfig.show" :title="confirmConfig.title" @hide="onConfirmCancel">
      <p class="mb-0">{{ confirmConfig.message }}</p>
      <template #footer>
        <BButton @click="onConfirmCancel">Cancel</BButton>
        <BButton :variant="confirmConfig.variant" @click="onConfirmOk">{{ confirmConfig.confirmText }}</BButton>
      </template>
    </BModal>

    <!-- Pivot Table Modal -->
    <PivotModal
      v-model="showPivotModal"
      :dataset-id="datasetId"
      :dataset-name="dataset?.name"
      :columns="columns"
      :selected-columns="selectedColumns"
      @close="showPivotModal = false"
    />

    <!-- Column Reorder Modal -->
    <ColumnReorderModal
      v-model="showColumnReorderModal"
      :columns="columns"
      :selected-columns="selectedColumns"
      @apply="applyColumnReorder"
    />

    <!-- AI Chat Modal -->
    <AiChatModal
      v-model="showAiChat"
      :dataset-id="datasetId"
      :columns="columns"
      :data="data"
      :total-rows="totalRows"
      :agent-options="agentOptions"
    />

  <!-- Change Type Modal -->
  <ChangeTypeModal
    v-model="showChangeTypeModal"
    :selected-columns="effectiveSelectedColumns"
    :dataset-id="datasetId"
    :operating="operating"
    @apply="applyChangeType"
  />

  <!-- Value Mapping Modal -->
  <ValueMappingModal
    v-model="showValueMappingModal"
    :column="selectedColumns[0] || ''"
    :dataset-id="datasetId"
    :unique-values="getValueMappingUniqueValues()"
    :operating="operating"
    @apply="applyValueMapping"
  />

    <!-- History Sidebar -->
    <div v-if="showHistory" class="history-sidebar">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h6 class="mb-0"><i class="bi bi-clock-history me-2"></i>Operation History</h6>
        <div class="d-flex gap-1">
          <BButton size="sm" variant="outline-success" @click="showExportRecipe = true" title="Export operations">
            <i class="bi bi-download"></i>
          </BButton>
          <BButton size="sm" variant="outline-primary" @click="showImportRecipe = true" title="Import operations">
            <i class="bi bi-upload"></i>
          </BButton>
          <BButton size="sm" variant="outline-secondary" @click="showHistory = false">
            <i class="bi bi-x-lg"></i>
          </BButton>
        </div>
      </div>
      
      <div v-if="operations.length === 0" class="text-muted text-center py-4">
        <i class="bi bi-inbox fs-4"></i>
        <p class="small mb-0">No operations yet</p>
      </div>
      
      <div v-else class="operation-list" style="max-height: 70vh; overflow-y: auto;">
        <div class="d-flex justify-content-between align-items-center mb-2 px-1">
          <div class="form-check">
            <input class="form-check-input" type="checkbox" id="select-all-ops" :checked="allOpsSelected" @change="toggleAllOps">
            <label class="form-check-label small" for="select-all-ops">Select all</label>
          </div>
          <div class="d-flex gap-1">
            <BButton v-if="redoableSelectedCount > 0" size="sm" variant="outline-success" @click="redoSelectedOps">
              <i class="bi bi-arrow-clockwise me-1"></i>Redo {{ redoableSelectedCount }}
            </BButton>
            <BButton v-if="undoableSelectedCount > 0" size="sm" variant="outline-warning" @click="undoSelectedOps">
              <i class="bi bi-arrow-counterclockwise me-1"></i>Undo {{ undoableSelectedCount }}
            </BButton>
            <BButton v-if="deletableSelectedCount > 0" size="sm" variant="outline-danger" @click="deleteSelectedOps" title="Delete selected undone operations">
              <i class="bi bi-trash me-1"></i>Delete {{ deletableSelectedCount }}
            </BButton>
          </div>
        </div>
        <div v-for="op in operations" :key="op.id" class="card mb-2">
          <div class="card-body py-2 px-3">
            <div class="d-flex justify-content-between align-items-start">
              <div class="d-flex align-items-start gap-2">
                <input
                  class="form-check-input mt-1"
                  type="checkbox"
                  :checked="selectedOpIds.includes(op.id)"
                  @change="toggleOpSelection(op.id)"
                >
                <div>
                  <div class="d-flex align-items-center gap-1">
                    <span class="badge" :class="op.is_undone ? 'bg-secondary' : 'bg-primary'">
                      {{ op.operation_type }}
                    </span>
                    <button class="btn btn-sm btn-link text-muted p-0" @click="showOpDetails(op)" title="View details">
                      <i class="bi bi-info-circle"></i>
                    </button>
                  </div>
                  <small class="text-muted d-block mt-1">
                    {{ formatDate(op.created_at) }}
                  </small>
                </div>
              </div>
              <div class="d-flex align-items-center gap-1">
                <BButton v-if="!op.is_undone" size="sm" variant="outline-warning" @click="undoOperation(op.id)" title="Undo this operation">
                  Undo
                </BButton>
                <BButton v-if="op.is_undone" size="sm" variant="outline-success" @click="redoOperation(op.id)" title="Redo this operation">
                  <i class="bi bi-arrow-clockwise"></i>
                </BButton>
                <BButton v-if="op.is_undone" size="sm" variant="outline-danger" @click="deleteOperation(op.id)" title="Delete this record">
                  <i class="bi bi-trash"></i>
                </BButton>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getApiUrl } from '@/utils/api'
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { BButton, BFormSelect, BFormInput, BFormTextarea, BFormFile, BFormGroup, BBadge, BModal, BDropdown, BDropdownItem, BDropdownItemButton, BDropdownDivider } from 'bootstrap-vue-next'
import DataTable from '@/components/DataTable.vue'
import PromptModal from '@/components/PromptModal.vue'
import OperationConfirmModal from '@/components/OperationConfirmModal.vue'
import AiCleanModal from '@/components/AiCleanModal.vue'
import AiChatModal from '@/components/AiChatModal.vue'
import FuzzyMatchModal from '@/components/FuzzyMatchModal.vue'
import ProfileModal from '@/components/ProfileModal.vue'
import ColumnReorderModal from '@/components/ColumnReorderModal.vue'
import ChangeTypeModal from '@/components/ChangeTypeModal.vue'
import ExtractPatternModal from '@/components/ExtractPatternModal.vue'
import ValueMappingModal from '@/components/ValueMappingModal.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const datasetId = computed(() => route.params.datasetId)

// Breadcrumb items - computed based on project and dataset
const projectId = computed(() => route.params.id)
const breadcrumbItems = computed(() => [
  { label: 'Projects', path: '/projects', icon: 'bi bi-folder' },
  { label: 'Project', path: `/projects/${projectId.value}`, icon: 'bi bi-folder2' },
  { label: dataset.value?.name || 'Dataset', icon: 'bi bi-table' }
])

const apiUrl = getApiUrl()
const toast = useToast()

const loading = ref(true)
const dataset = ref(null)
const data = ref([])
const columns = ref([])
const operations = ref([])
const limit = ref(10)
const page = ref(1)
const totalRows = ref(0)
const jumpToPage = ref(null)

// Pagination computed properties
const startRow = computed(() => Math.min((page.value - 1) * limit.value + 1, totalRows.value))
const endRow = computed(() => Math.min(page.value * limit.value, totalRows.value))

const searchQuery = ref('')
const showRowFilterModal = ref(false)
const dataTableRef = ref(null)
const hiddenColumns = ref([])
const applyToHiddenColumns = ref(false) // Whether to apply operations to hidden columns
const rowFilters = ref({})
const rowSelectMode = ref(false)
const operationRowScope = ref('all') // 'all' | 'selected'
async function onHiddenColumnsChanged(newHiddenColumns) {
  hiddenColumns.value = newHiddenColumns
}

function unhideAllColumns() {
  hiddenColumns.value = []
}

function toggleVisibility(key) {
  const idx = hiddenColumns.value.indexOf(key)
  if (idx >= 0) {
    hiddenColumns.value.splice(idx, 1)
  } else {
    hiddenColumns.value.push(key)
  }
}

// Filter selected columns to exclude hidden ones (unless applyToHiddenColumns is enabled)
const effectiveSelectedColumns = computed(() => {
  if (applyToHiddenColumns.value) {
    return selectedColumns.value
  }
  return selectedColumns.value.filter(col => !hiddenColumns.value.includes(col))
})
const showCellEdit = ref(false)
const cellEdit = ref({ row: 0, column: '', value: '' })
const showEncodingModal = ref(false)
const encodingOp = ref('')
const encodingParams = ref({ prefix: '', mappingJson: '{}', n_bins: 5, strategy: 'equal_width' })
const encodingPreview = ref([])
const encodingConfig = ref({ title: '', description: '' })
const showAddRecords = ref(false)
const addMode = ref('single')
const singleRow = ref({})
const pendingRows = ref([])
const csvText = ref('')
const jsonText = ref('')
const showRowIndex = ref(false)
const multiSort = ref(false)
const sortKeys = ref([]) // Server-side sort state: [{ key: 'name', dir: 'asc' }, ...]
const showFooter = ref(false)
const footerStats = ref({})
const showTableSettings = ref(false)
// Column multi-filter state
const enableColumnFilter = ref(false)
const columnFilterState = ref({}) // { columnName: [selectedValues] }
const columnUniqueValues = ref({}) // { columnName: [{value, count}] }
const columnUniqueCounts = ref({}) // { columnName: totalUnique }
const fetchingUniqueValues = ref({}) // { columnName: boolean }
// const footerConfig = ref({})
const fetchingStats = ref(false)

function onRowSelectToggle() {
  if (!rowSelectMode.value) selectedRowIndices.value = []
}

async function onShowFooterToggle() {
  if (showFooter.value) {
    await fetchFooterStats()
  }
}

async function fetchFooterStats() {
  if (fetchingStats.value || !datasetId.value) return
  fetchingStats.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/profile`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json();
      if (data && data.status === 'success') {
        const statsObj = {}
        for (const col of data.columns || []) {
          const dtype = col?.dtype || ''
          const isNumeric = dtype.startsWith('int') || dtype.startsWith('float')
          statsObj[col.name] = {
            is_numeric: isNumeric,
            stats: {
              null_count: col.null_count ?? 0,
              unique: col.unique_count || 0,
              ...col.stats
            }
          }
        }
        footerStats.value = statsObj
      }
    } else {
      toast.error('Failed to load footer stats')
      showFooter.value = false
    }
  } catch (e) {
    console.error(e)
    toast.error('Failed to load footer stats')
    showFooter.value = false
  } finally {
    fetchingStats.value = false
  }
}

const ENCODING_CONFIGS = {
  one_hot: { title: 'One-Hot Encoding', description: 'Creates binary (0/1) columns for each unique value in the selected column. Useful for categorical features in ML models.', defaults: { prefix: '' } },
  label: { title: 'Label Encoding', description: 'Maps each unique category to an integer (0, 1, 2…). Sorted alphabetically. Useful for ordinal data or tree-based models.', defaults: {} },
  map: { title: 'Map Values', description: 'Replace values using a custom dictionary. Useful for standardizing categories or recoding values.', defaults: { mappingJson: '{}' } },
  bin: { title: 'Binning / Discretization', description: 'Group continuous numeric values into discrete bins. Equal-width creates uniform intervals; equal-frequency puts roughly the same count in each bin.', defaults: { n_bins: 5, strategy: 'equal_width' } },
}

function openEncodingModal(op) {
  if (!effectiveSelectedColumns.value.length) {
    toast.warning('Select a column first')
    return
  }
  encodingOp.value = op
  const config = ENCODING_CONFIGS[op]
  encodingConfig.value = { title: config.title, description: config.description }
  encodingParams.value = { ...config.defaults }
  encodingPreview.value = []
  showEncodingModal.value = true
  // Generate preview from current data
  if (op === 'one_hot') {
    encodingParams.value.prefix = effectiveSelectedColumns.value[0]
    const col = effectiveSelectedColumns.value[0]
    const unique = [...new Set(data.value.map(r => r[col]).filter(v => v != null))]
    encodingPreview.value = [{ ...Object.fromEntries(unique.map(v => [`${encodingParams.value.prefix}_${v}`, 1])) }]
  } else if (op === 'label') {
    const col = effectiveSelectedColumns.value[0]
    const unique = [...new Set(data.value.map(r => r[col]).filter(v => v != null))].sort()
    encodingPreview.value = unique.map((v, i) => ({ value: v, label: i }))
  } else if (op === 'bin') {
    const col = effectiveSelectedColumns.value[0]
    encodingPreview.value = data.value.slice(0, 5).map(r => ({ original: r[col], binned: '...' }))
  }
}

async function applyEncoding() {
  if (!effectiveSelectedColumns.value.length) return
  const op = encodingOp.value
  const body = { column: effectiveSelectedColumns.value[0], operation: op }

  if (op === 'one_hot') {
    body.prefix = encodingParams.value.prefix || effectiveSelectedColumns.value[0]
  } else if (op === 'map') {
    try {
      body.mapping = JSON.parse(encodingParams.value.mappingJson)
    } catch {
      toast.error('Invalid JSON in mapping')
      return
    }
  } else if (op === 'bin') {
    body.n_bins = encodingParams.value.n_bins || 5
    body.strategy = encodingParams.value.strategy || 'equal_width'
  }

  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/encoding`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(body)
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message || 'Encoding applied')
      showEncodingModal.value = false
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Encoding failed')
    }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

function resolveAbsoluteRowIndex(displayRowIndex) {
  // When server-side filters are active, data rows are non-contiguous slices
  // of the full dataset. Use filteredMatchingIndices to map display position
  // to the original dataset row index.
  if (filteredMatchingIndices.value && filteredMatchingIndices.value.length > 0) {
    const pageOffset = (page.value - 1) * limit.value
    const indexInMatching = pageOffset + displayRowIndex
    if (indexInMatching < filteredMatchingIndices.value.length) {
      return filteredMatchingIndices.value[indexInMatching]
    }
  }
  // No filter active: rows are a contiguous slice, use arithmetic offset
  return (page.value - 1) * limit.value + displayRowIndex
}

function openCellEditor({ row, column, value }) {
  const absoluteRow = resolveAbsoluteRowIndex(row)
  cellEdit.value = { row: absoluteRow, column, value: String(value ?? '') }
  showCellEdit.value = true
}

async function saveCellEdit() {
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/update-cell`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ row_index: cellEdit.value.row, column: cellEdit.value.column, value: cellEdit.value.value })
    })
    const data = await res.json()
    if (res.ok) {
      if (data.status === 'failed') {
        toast.error(data.message || 'Update failed — check the value format')
      } else {
        toast.success('Cell updated')
        showCellEdit.value = false
        await refreshData()
      }
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Update failed')
    }
  } catch (e) { 
    toast.error(e.message) 
  }
  finally { operating.value = false }
}
const selectedRowIndices = ref([])
const filteredMatchingIndices = ref(null)
const filteredTotalMatching = ref(null)
const promptConfig = ref({ show: false, title: '', message: '', defaultValue: '', inputType: 'text', confirmText: 'OK' })
const confirmConfig = ref({ show: false, title: 'Confirm', message: '', confirmText: 'Confirm', variant: 'primary' })
let promptResolve = null
let confirmResolve = null
const showProfile = ref(false)
const showCompare = ref(false)
const showHistory = ref(false)
const showPivotModal = ref(false)
const showColumnReorderModal = ref(false)
const showChangeTypeModal = ref(false)
const exportZip = ref(false)
const importText = ref('')
const importFile = ref(null)
const importPreview = ref(null)
const importResults = ref(null)
const importMode = ref('paste')
const importError = ref('')
const showClipboardImport = ref(false)
const showFillnaModal = ref(false)
const showStructuralAiModal = ref(false)
const showFuzzyMatchModal = ref(false)
const showDataAiModal = ref(false)
const showAiChat = ref(false)
const showExportRecipe = ref(false)
const showImportRecipe = ref(false)
const agents = ref([])
const agentOptions = computed(() => [
  { value: null, text: 'Select an AI Agent…' },
  ...agents.value.map(a => ({ value: a.id, text: `${a.name} (${a.provider}/${a.model})` }))
])
const profileData = ref(null)
const comparing = ref(false)
const compareOpId = ref(null)
const comparisonResult = ref(null)
const nullCount = ref(0)
const selectedColumns = ref([])  // Selected columns (click on table headers)
const selectedRows = ref([])  // Selected rows
const batchProgress = ref(null)
const fuzzyAiContext = ref(null)

// Load selected columns from localStorage (dataset-specific)
const loadSelectedColumns = () => {
  try {
    const key = `dataViewer-selectedColumns-${datasetId.value}`
    const saved = localStorage.getItem(key)
    if (saved) {
      const parsed = JSON.parse(saved)
      // Filter to only include columns that still exist (in case columns changed)
      if (columns.value.length > 0) {
        const existingColumnFields = columns.value.map(c => c.field)
        selectedColumns.value = parsed.filter(col => existingColumnFields.includes(col))
      } else {
        selectedColumns.value = parsed
      }
    }
  } catch (e) {
    console.warn('Failed to load selected columns from localStorage:', e)
  }
}

// Save selected columns to localStorage (dataset-specific)
const saveSelectedColumns = () => {
  try {
    const key = `dataViewer-selectedColumns-${datasetId.value}`
    localStorage.setItem(key, JSON.stringify(selectedColumns.value))
  } catch (e) {
    console.warn('Failed to save selected columns to localStorage:', e)
  }
}

// Computed fields for BTable - disable sorting to allow column selection
const tableFields = computed(() => {
  return columns.value.map(col => ({
    key: col.field,
    label: col.label,
    sortable: false
  }))
})

// Selected row keys for BTable
const selectedRowKeys = computed(() => {
  return selectedRows.value.map(row => row._index ?? JSON.stringify(row))
})
const showColumnSelector = ref(false)
const fillValue = ref('')
const showExtractJsonModal = ref(false)
const extractJsonKey = ref('')
const extractJsonSamples = ref([])
const extractJsonSuggestedKeys = ref([])
const showExtractPatternModal = ref(false)
const extractPatternSamples = ref([])
const showFindReplaceModal = ref(false)
const showValueMappingModal = ref(false)
const showOpConfirm = ref(false)
const opConfirmConfig = ref({ title: '', description: '', operation: '', params: {}, options: [], handler: null })
const showMergeModal = ref(false)
const mergeColumns = ref([])
const mergeNewColumn = ref('')
const mergeDelimiter = ref(' ')
const showSplitModal = ref(false)
const splitDelimiter = ref('')
const splitNewColumns = ref([])
const splitNewColName = ref('')
const showCloneModal = ref(false)
const cloneNewName = ref('')
const findValue = ref('')
const replaceValue = ref('')
const findReplaceRegex = ref(false)
const findReplaceCaseSensitive = ref(true)
const canUndo = computed(() => operations.value.some(op => !op.is_undone))
const canRedo = computed(() => operations.value.some(op => op.is_undone))
const selectedOpIds = ref([])
const showOpDetailsModal = ref(false)
const selectedOp = ref(null)
const allOpsSelected = computed(() => {
  return operations.value.length > 0 && operations.value.every(op => selectedOpIds.value.includes(op.id))
})
const deletableSelectedCount = computed(() => {
  return selectedOpIds.value.filter(id => {
    const op = operations.value.find(o => o.id === id)
    return op && op.is_undone
  }).length
})

const redoableSelectedCount = computed(() => {
  return selectedOpIds.value.filter(id => {
    const op = operations.value.find(o => o.id === id)
    return op && op.is_undone
  }).length
})
const undoableSelectedCount = computed(() => {
  return selectedOpIds.value.filter(id => {
    const op = operations.value.find(o => o.id === id)
    return op && !op.is_undone
  }).length
})
const operating = ref(false)
const clipboardData = ref('')
const clipboardDatasetName = ref('')

const limitOptions = [
  { value: 10, text: '10 rows' },
  { value: 25, text: '25 rows' },
  { value: 50, text: '50 rows' },
  { value: 100, text: '100 rows' },
  { value: 250, text: '250 rows' },
  { value: 500, text: '500 rows' }
]

const totalPages = computed(() => Math.ceil(totalRows.value / limit.value))

// Page numbers to display in pagination (shows up to 7 pages with ellipsis)
const pageNumbers = computed(() => {
  const total = totalPages.value
  const current = page.value
  const pages = []
  
  if (total <= 7) {
    // Show all pages if 7 or fewer
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    // Always show first page
    pages.push(1)
    
    if (current > 3) {
      pages.push('...')
    }
    
    // Show pages around current
    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)
    
    for (let i = start; i <= end; i++) {
      if (!pages.includes(i)) pages.push(i)
    }
    
    if (current < total - 2) {
      pages.push('...')
    }
    
    // Always show last page
    if (!pages.includes(total)) pages.push(total)
  }
  
  return pages
})
const progressBarClass = computed(() => {
  if (!batchProgress.value) return ''
  const p = batchProgress.value
  if (p.status === 'done') return 'bg-info'
  if (p.status === 'error') return 'bg-danger'
  if (p.failed > 0) return 'bg-warning'
  return 'bg-success'
})

function nextPage() {
  if (page.value < totalPages.value) {
    page.value++
    refreshData()
  }
}

function goToPage(p) {
  if (p < 1) return
  const maxPage = Math.ceil(totalRows.value / limit.value)
  if (p > maxPage) return
  page.value = p
  refreshData()
}

const columnOptions = computed(() => columns.value.map(c => ({ value: c.field, text: c.label })))

// Toggle column selection (click on table header)
function toggleColumnSelection(field) {
  const idx = selectedColumns.value.indexOf(field)
  if (idx === -1) {
    selectedColumns.value.push(field)
  } else {
    selectedColumns.value.splice(idx, 1)
  }
}

// Handle BTable row selection
function onRowSelected(rows) {
  selectedRows.value = rows
}

// Handle DataTable row click
function onRowClicked({ item, index }) {
  // Toggle selection or handle as needed
  const idx = selectedRows.value.findIndex(r => JSON.stringify(r) === JSON.stringify(item))
  if (idx >= 0) {
    selectedRows.value.splice(idx, 1)
  } else {
    selectedRows.value.push(item)
  }
}

// Handle DataTable pagination
function goToPrev() {
  if (page.value > 1) {
    page.value--
    refreshData()
  }
}

function goToNext() {
  const maxPage = Math.ceil(totalRows.value / limit.value)
  if (page.value < maxPage) {
    page.value++
    refreshData()
  }
}

// Handle DataTable page change - just refresh data (v-model updates page)
function onPageChange(newPage) {
  refreshData()
}

// Handle DataTable header click (for future sorting)
function onHeadClicked(field) {
  // Toggle column selection when clicking column header
  toggleColumnSelection(field.key || field.field)
}

// Handle server-side sort: call backend sort API when sort changes
async function onSortChanged(newSortKeys) {
  if (newSortKeys.length === 0) {
    // Sort cleared — refresh data (server data reverts to original order on refresh)
    sortKeys.value = []
    await refreshData()
    return
  }
  sortKeys.value = [...newSortKeys]
  operating.value = true
  try {
    let body
    if (newSortKeys.length === 1) {
      // Single column sort: use backward-compatible format
      const { key, dir } = newSortKeys[0]
      body = { column: key, ascending: dir === 'asc', na_position: 'last' }
    } else {
      // Multi-column sort: use sort_keys format
      body = {
        sort_keys: newSortKeys.map(sk => ({ column: sk.key, ascending: sk.dir === 'asc' })),
        na_position: 'last',
      }
    }
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/sort`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(body)
    })
    if (res.ok) {
      const sortResult = await res.json()
      const sortDesc = newSortKeys.map(sk => `${sk.key} ${sk.dir === 'asc' ? '↑' : '↓'}`).join(', ')
      toast.success(`Sorted by ${sortDesc}`)
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Sort failed')
    }
  } catch (e) {
    toast.error(e.message)
  } finally {
    operating.value = false
  }
}

// Check if single-column only operation (like rename)
function isSingleColumnOnly(operation) {
  return ['rename'].includes(operation)
}

const operationOptions = computed(() => operations.value.map(op => ({ value: op.id, text: `${op.operation_type} - ${formatDate(op.created_at)}` })))

// Data from API (already paginated by server)
const paginatedData = computed(() => {
  // Data from API is already limited, no need to slice again
  return data.value
})

// Column filter computed properties
const hasColumnFilters = computed(() => Object.keys(columnFilterState.value).some(k => columnFilterState.value[k] && columnFilterState.value[k].length > 0))
const activeColumnFilterCount = computed(() => Object.keys(columnFilterState.value).filter(k => columnFilterState.value[k] && columnFilterState.value[k].length > 0).length)

// Filtered data (search) applied on top of paginated data
const hasActiveFilter = computed(() => Object.values(rowFilters.value).some(v => v && v.trim()) || hasColumnFilters.value)

const filteredData = computed(() => {
  let result = paginatedData.value
  // Search filter (always client-side, on top of current page data)
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(row => Object.values(row).some(val => String(val ?? '').toLowerCase().includes(q)))
  }
  // Note: when hasActiveFilter is true, data is already server-filtered
  // via refreshData's /filtered endpoint call. No client-side multi-column filter needed.
  return result
})

async function fetchAgents() {
  try {
    const res = await fetch(`${apiUrl}/api/agents/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      agents.value = Array.isArray(data) ? data : []
    }
  } catch (e) { /* silent */ }
}

onMounted(async () => {
   loadSelectedColumns()
   await refreshData()
   await fetchAgents()
   if (route.query.showProfile === 'true') showProfile.value = true
 })

// Watch for changes to selectedColumns and save to localStorage
watch(selectedColumns, (newVal) => {
   saveSelectedColumns()
}, { deep: true })

// Watch limit changes - reset to first page and refresh
watch(limit, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    page.value = 1
    refreshData()
  }
})

// Watch datasetId changes - reset state and reload data for new dataset
watch(datasetId, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    // Reset component state for the new dataset
    page.value = 1
    searchQuery.value = ''
    rowFilters.value = {}
    columnFilterState.value = {}
    selectedColumns.value = []
    selectedRowIndices.value = []
    hiddenColumns.value = []
    sortKeys.value = []
    operations.value = []
    loadSelectedColumns()
    refreshData()
  }
})

// Watch for compare modal
watch(showCompare, (val) => {
  if (!val) {
    comparisonResult.value = null
    compareOpId.value = null
  }
})

// Auto-switch row scope to 'selected' when rows are selected
watch(selectedRowIndices, (newVal) => {
    if (newVal.length > 0 && operationRowScope.value === 'all') {
      operationRowScope.value = 'selected'
    }
  })

// When multiSort is toggled off, clear any multi-sort keys (keep only first if any)
watch(multiSort, (newVal) => {
  if (!newVal && sortKeys.value.length > 1) {
    // Keep only the primary sort key when switching from multi to single sort
    sortKeys.value = [sortKeys.value[0]]
  }
})

// When operations change (after undo/redo), clear sort indicators if a sort was undone/redone
watch(operations, (newOps) => {
  if (sortKeys.value.length === 0) return
  // Check if the most recent non-undone sort operation matches our current sortKeys
  const activeSortOps = newOps.filter(op => op.operation_type === 'sort' && !op.is_undone)
  if (activeSortOps.length === 0 && sortKeys.value.length > 0) {
    // All sort operations have been undone — clear sort indicators
    sortKeys.value = []
  }
}, { deep: true })


async function refreshData() {
  loading.value = true
  try {
    const authHeader = { Authorization: `Bearer ${localStorage.getItem('token')}` }

    // Choose endpoint based on filter state
    let previewRes
    const hasSubstringFilters = Object.values(rowFilters.value).some(v => v && v.trim())
    if (hasSubstringFilters || hasColumnFilters.value) {
      const activeFilters = {}
      // Add substring filters (legacy format)
      for (const [k, v] of Object.entries(rowFilters.value)) {
        if (v && v.trim()) activeFilters[k] = v.trim()
      }
      // Add column selected_values filters (new format)
      for (const [col, selectedValues] of Object.entries(columnFilterState.value)) {
        if (selectedValues && selectedValues.length > 0) {
          activeFilters[col] = { selected_values: selectedValues }
        }
      }
      previewRes = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/filtered?limit=${limit.value}&page=${page.value}`, {
        method: 'POST',
        headers: { ...authHeader, 'Content-Type': 'application/json' },
        body: JSON.stringify(activeFilters)
      })
    } else {
      previewRes = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/preview?limit=${limit.value}&page=${page.value}`, {
        headers: authHeader
      })
    }

    // Always fetch operations (parallel with preview when no filter)
    const opsPromise = fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations`, { headers: authHeader })

    if (previewRes.ok) {
      const preview = await previewRes.json()
      data.value = preview.preview_data || []
      columns.value = (preview.columns || []).map(col => ({ field: col.name, label: col.name }))
      dataset.value = preview
      // Normalize data row key order to match columns.value order to prevent column mismatch
      if (data.value.length > 0 && columns.value.length > 0) {
        const columnOrder = columns.value.map(c => c.field)
        data.value = data.value.map(row => {
          const orderedRow = {}
          for (const key of columnOrder) {
            if (key in row) {
              orderedRow[key] = row[key]
            }
          }
          return orderedRow
        })
      }

      if (hasSubstringFilters || hasColumnFilters.value) {
        filteredMatchingIndices.value = preview.matching_indices || null
        filteredTotalMatching.value = preview.total_matching ?? null
        totalRows.value = preview.total_matching || 0
      } else {
        filteredMatchingIndices.value = null
        filteredTotalMatching.value = null
        totalRows.value = preview.row_count || 0
      }
    }

    const opsRes = await opsPromise
    if (opsRes.ok) {
      const opsData = await opsRes.json()
      operations.value = opsData.operations || opsData || []
      selectedOpIds.value = []
    }
    
    const profileRes = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/profile`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (profileRes.ok) {
      profileData.value = await profileRes.json()
      nullCount.value = profileData.value.columns?.reduce((sum, c) => sum + c.null_count, 0) || 0
    }
    // Invalidate unique values cache since data may have changed
    columnUniqueValues.value = {}
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function loadComparison() {
  if (!compareOpId.value) return
  comparing.value = true
  comparisonResult.value = null
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/compare/${compareOpId.value}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      comparisonResult.value = await res.json()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed to load comparison')
    }
  } catch (e) { 
    console.error(e)
    toast.error('Failed to load comparison')
  }
  finally { comparing.value = false }
}

async function applyOperation(endpoint, params) {
  if (!effectiveSelectedColumns.value || effectiveSelectedColumns.value.length === 0) {
    toast.warning('No columns selected'); return
  }
  const col = effectiveSelectedColumns.value[0]
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ column: col, ...params })
    })
    if (res.ok) { 
      const data = await res.json()
      toast.success(data.message || 'Operation applied successfully')
      await refreshData() 
    }
    else { const err = await res.json(); toast.error(err.detail || 'Operation failed') }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false; showFillnaModal.value = false }
}

async function applyStringOp(operation) {
  if (!effectiveSelectedColumns.value || effectiveSelectedColumns.value.length === 0) {
    toast.warning('No columns selected'); return
  }
  operating.value = true
  try {
    const body = { 
      columns: effectiveSelectedColumns.value, 
      operation,
      row_indices: operationRowScope.value === 'selected' ? selectedRowIndices.value : undefined
    }
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/string-operations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(body)
    })
    if (res.ok) { 
      const data = await res.json()
      toast.success(data.message || 'Operation applied successfully')
      await refreshData() 
    }
    else { const err = await res.json(); toast.error(err.detail || 'Operation failed') }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

// Change type modal
function openChangeTypeModal() {
  if (!effectiveSelectedColumns.value || effectiveSelectedColumns.value.length === 0) {
    toast.warning('No columns selected'); return
  }
  showChangeTypeModal.value = true
}

async function applyChangeType(payload) {
  operating.value = true
  try {
    const body = {
      column: payload.column,
      target_type: payload.targetType,
      error_handling: payload.errorHandling,
    }
    if (payload.errorHandling === 'fallback' && payload.fallbackValue != null) {
      body.fallback_value = payload.fallbackValue
    }
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/change-type`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(body),
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message || 'Type changed successfully')
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Type change failed')
    }
  } catch (e) {
    toast.error(e.message)
  } finally {
    operating.value = false
  }
}

function openValueMappingModal() {
  if (!effectiveSelectedColumns.value || effectiveSelectedColumns.value.length !== 1) {
    toast.warning('Select exactly 1 column to map values')
    return
  }
  showValueMappingModal.value = true
}

function getValueMappingUniqueValues() {
  const col = selectedColumns.value[0]
  if (!col || !data.value.length) return []
  const unique = [...new Set(data.value.map(r => r[col]).filter(v => v != null))]
  return unique.map(v => String(v))
}

async function applyValueMapping(payload) {
  operating.value = true
  try {
    const body = {
      column: payload.column,
      mappings: payload.mappings,
      missing_value_action: payload.missing_value_action,
      missing_value_fill: payload.missing_value_fill,
      default_value: payload.default_value,
      row_indices: operationRowScope.value === 'selected' ? selectedRowIndices.value : undefined,
    }
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/map-values`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(body),
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message || 'Value mapping applied')
      showValueMappingModal.value = false
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Value mapping failed')
    }
  } catch (e) {
    toast.error(e.message)
  } finally {
    operating.value = false
  }
}

// Merge columns
function openMergeColumnsModal() {
  mergeColumns.value = effectiveSelectedColumns.value.length >= 2 ? [...effectiveSelectedColumns.value] : []
  mergeNewColumn.value = ''
  mergeDelimiter.value = ' '
  showMergeModal.value = true
}

async function applyMerge() {
  if (mergeColumns.value.length < 2 || !mergeNewColumn.value) return
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/merge-columns`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ columns: mergeColumns.value, new_column: mergeNewColumn.value, delimiter: mergeDelimiter.value })
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message || 'Columns merged')
      showMergeModal.value = false
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Merge failed')
    }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

// Split column
function openSplitColumnModal() {
  if (effectiveSelectedColumns.value.length !== 1) {
    toast.warning('Select exactly 1 column to split')
    return
  }
  splitDelimiter.value = ''
  splitNewColumns.value = []
  splitNewColName.value = ''
  showSplitModal.value = true
}

function addSplitColumn() {
  if (splitNewColName.value.trim()) {
    splitNewColumns.value.push(splitNewColName.value.trim())
    splitNewColName.value = ''
  }
}

async function applySplit() {
  if (!splitDelimiter.value || splitNewColumns.value.length < 2) return
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/split-column`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ column: effectiveSelectedColumns.value[0], delimiter: splitDelimiter.value, new_columns: splitNewColumns.value })
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message || 'Column split')
      showSplitModal.value = false
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Split failed')
    }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

// Clone column
function openCloneColumnModal() {
  if (effectiveSelectedColumns.value.length !== 1) {
    toast.warning('Select exactly 1 column to clone')
    return
  }
  cloneNewName.value = effectiveSelectedColumns.value[0] + '_copy'
  showCloneModal.value = true
}

async function applyCloneColumn() {
  if (!cloneNewName.value || effectiveSelectedColumns.value.length !== 1) return
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/duplicate-column`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ source_column: effectiveSelectedColumns.value[0], new_column: cloneNewName.value })
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message || 'Column cloned')
      showCloneModal.value = false
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Clone failed')
    }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

function openExtractJsonModal() {
  if (!effectiveSelectedColumns.value || effectiveSelectedColumns.value.length !== 1) {
    toast.warning('Select exactly 1 column to extract JSON from')
    return
  }
  // Get sample values from current data
  const col = effectiveSelectedColumns.value[0]
  const samples = data.value.map(row => row[col]).filter(v => v != null).slice(0, 5)
  extractJsonSamples.value = samples.map(s => String(s))

  // Auto-detect keys from first valid JSON sample
  extractJsonSuggestedKeys.value = []
  for (const s of samples) {
    try {
      const obj = JSON.parse(String(s))
      if (typeof obj === 'object' && obj !== null && !Array.isArray(obj)) {
        extractJsonSuggestedKeys.value = Object.keys(obj)
        break
      }
    } catch { /* not JSON */ }
  }

  extractJsonKey.value = extractJsonSuggestedKeys.value[0] || ''
  showExtractJsonModal.value = true
}

async function applyExtractJson() {
  if (!extractJsonKey.value) { toast.warning('Enter a key'); return }
  const col = effectiveSelectedColumns.value[0]
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/extract-json`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ column: col, key: extractJsonKey.value })
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message || 'JSON values extracted')
      showExtractJsonModal.value = false
      await refreshData()
    } else { const err = await res.json(); toast.error(err.detail || 'Extraction failed') }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

function openExtractPatternModal() {
  if (!effectiveSelectedColumns.value || effectiveSelectedColumns.value.length !== 1) {
    toast.warning('Select exactly 1 column to extract pattern from')
    return
  }
  const col = effectiveSelectedColumns.value[0]
  extractPatternSamples.value = data.value.map(row => row[col]).filter(v => v != null).slice(0, 5).map(s => String(s))
  showExtractPatternModal.value = true
}

async function applyExtractPattern(payload) {
  if (!payload.pattern) { toast.warning('Enter a regex pattern'); return }
  const col = effectiveSelectedColumns.value[0]
  operating.value = true
  try {
    const body = {
      column: col,
      pattern: payload.pattern,
      case_sensitive: payload.case_sensitive,
      row_indices: operationRowScope.value === 'selected' ? selectedRowIndices.value : undefined,
    }
    if (payload.new_column) {
      body.new_column = payload.new_column
    }
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/extract-pattern`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(body)
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message || 'Pattern extracted')
      showExtractPatternModal.value = false
      await refreshData()
    } else { const err = await res.json(); toast.error(err.detail || 'Pattern extraction failed') }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

async function applyFindReplace() {
  if (!effectiveSelectedColumns.value.length) { toast.warning('Select columns first'); return }
  if (!findValue.value) { toast.warning('Enter a find value'); return }
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/find-replace`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({
        columns: effectiveSelectedColumns.value,
        find: findValue.value,
        replace: replaceValue.value,
        regex: findReplaceRegex.value,
        case_sensitive: findReplaceCaseSensitive.value,
        row_indices: operationRowScope.value === 'selected' ? selectedRowIndices.value : undefined,
      })
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message)
      showFindReplaceModal.value = false
      await refreshData()
    } else { const err = await res.json(); toast.error(err.detail || 'Find & Replace failed') }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

async function applyDatetimeOp(operation) {
  if (!effectiveSelectedColumns.value || effectiveSelectedColumns.value.length === 0) {
    toast.warning('No columns selected'); return
  }
  operating.value = true
  try {
    const body = { 
      columns: effectiveSelectedColumns.value, 
      operation,
      row_indices: operationRowScope.value === 'selected' ? selectedRowIndices.value : undefined
    }
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/datetime-operations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(body)
    })
    if (res.ok) { 
      const data = await res.json()
      toast.success(data.message || 'Operation applied successfully')
      await refreshData() 
    }
    else { const err = await res.json(); toast.error(err.detail || 'Operation failed') }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}
async function applyStructuralOp(operation) {
  if (operation === 'add_column') {
    const newName = await showPrompt({ title: 'Add Column', message: 'Enter new column name:' })
    if (!newName) return
    const defaultValue = await showPrompt({ title: 'Add Column', message: `Default value for "${newName}" (leave empty for blank):` }) ?? ''
    operating.value = true
    try {
      const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/structural`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({ operation: 'add_column', new_name: newName, default_value: defaultValue })
      })
      if (res.ok) {
        const data = await res.json()
        toast.success(data.message || `Column "${newName}" added`)
        await refreshData()
      }
      else { const err = await res.json(); toast.error(err.detail || 'Operation failed') }
    } catch (e) { toast.error(e.message) }
    finally { operating.value = false }
  } else if (operation === 'rename') {
    // Rename is single-column only
    if (effectiveSelectedColumns.value.length !== 1) {
      toast.warning('Select exactly 1 column to rename'); return
    }
    const currentName = effectiveSelectedColumns.value[0]
    const newName = await showPrompt({ title: 'Rename Column', message: 'Enter new column name:', defaultValue: currentName })
    if (!newName || newName === currentName) return
    const col = effectiveSelectedColumns.value[0]
    await applyOperation('structural', { operation, column: col, new_name: newName })
  } else if (operation === 'astype') {
    openChangeTypeModal()
  } else if (operation === 'drop') {
    if (!effectiveSelectedColumns.value || effectiveSelectedColumns.value.length === 0) {
      toast.warning('No columns selected'); return
    }
    if (!(await showConfirm({ title: 'Delete Columns', message: `Delete ${effectiveSelectedColumns.value.length} column(s)?`, variant: 'danger', confirmText: 'Delete' }))) return
    operating.value = true
    try {
      const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/structural`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({ operation, columns: effectiveSelectedColumns.value })
      })
      if (res.ok) { 
        const data = await res.json()
        toast.success(data.message || 'Operation applied successfully')
        await refreshData() 
        selectedColumns.value = []
      }
      else { const err = await res.json(); toast.error(err.detail || 'Operation failed') }
    } catch (e) { toast.error(e.message) }
    finally { operating.value = false }
  }
}
async function applyNumericOp(operation) {
  if (!effectiveSelectedColumns.value || effectiveSelectedColumns.value.length === 0) {
    toast.warning('No columns selected'); return
  }
  operating.value = true
  try {
    const body = { 
      columns: effectiveSelectedColumns.value, 
      operation,
      row_indices: operationRowScope.value === 'selected' ? selectedRowIndices.value : undefined
    }
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/numeric`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(body)
    })
    if (res.ok) { 
      const data = await res.json()
      toast.success(data.message || 'Operation applied successfully')
      await refreshData() 
    }
    else { const err = await res.json(); toast.error(err.detail || 'Operation failed') }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}
async function applyFillnaStat(method) {
  operating.value = true
  try {
    const cols = effectiveSelectedColumns.value.length ? effectiveSelectedColumns.value : undefined
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/fillna`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ method, columns: cols })
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message || `Filled with ${method}`)
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Operation failed')
    }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

const OP_CONFIGS = {
  // Fillna
  'fillna-drop': { title: 'Drop Rows with Nulls', description: 'Removes all rows that contain any null/missing values. This cannot be undone easily for large datasets.', operation: 'fillna', params: { method: 'drop' }, options: [] },
  'fillna-mean': { title: 'Fill with Mean', description: 'Replaces null values in numeric columns with the column mean (average). Only affects numeric columns.', operation: 'fillna', params: { method: 'mean' }, options: [] },
  'fillna-median': { title: 'Fill with Median', description: 'Replaces null values in numeric columns with the column median. More robust to outliers than mean.', operation: 'fillna', params: { method: 'median' }, options: [] },
  'fillna-mode': { title: 'Fill with Mode', description: 'Replaces null values with the most frequent value in each column.', operation: 'fillna', params: { method: 'mode' }, options: [] },
  'fillna-forward': { title: 'Forward Fill', description: 'Propagates the last valid observation forward to fill null values.', operation: 'fillna', params: { method: 'forward' }, options: [] },
  'fillna-backward': { title: 'Backward Fill', description: 'Propagates the next valid observation backward to fill null values.', operation: 'fillna', params: { method: 'backward' }, options: [] },
  // String ops
  'string-strip': { title: 'Trim Whitespace', description: 'Removes leading and trailing whitespace from text values.', operation: 'string-operations', params: { operation: 'strip' }, options: [] },
  'string-lower': { title: 'Lowercase', description: 'Converts all text to lowercase.', operation: 'string-operations', params: { operation: 'lower' }, options: [] },
  'string-upper': { title: 'Uppercase', description: 'Converts all text to UPPERCASE.', operation: 'string-operations', params: { operation: 'upper' }, options: [] },
  'string-title': { title: 'Title Case', description: 'Capitalizes The First Letter Of Each Word.', operation: 'string-operations', params: { operation: 'title' }, options: [] },
  'string-capitalize': { title: 'Capitalize', description: 'Capitalizes only the first letter of each value.', operation: 'string-operations', params: { operation: 'capitalize' }, options: [] },
  // Date ops
  'datetime-parse-datetime': { title: 'Parse Datetime', description: 'Attempts to parse text values into datetime format.', operation: 'datetime-operations', params: { operation: 'parse-datetime' }, options: [] },
  'datetime-extract-year': { title: 'Extract Year', description: 'Extracts the year component from datetime values into a new column.', operation: 'datetime-operations', params: { operation: 'extract-year' }, options: [] },
  'datetime-extract-month': { title: 'Extract Month', description: 'Extracts the month component from datetime values into a new column.', operation: 'datetime-operations', params: { operation: 'extract-month' }, options: [] },
  // Numeric ops
  'numeric-round': { title: 'Round Numbers', description: 'Rounds numeric values to a specified number of decimal places.', operation: 'numeric', params: { operation: 'round' }, options: [{ key: 'decimals', label: 'Decimal places', type: 'range', min: 0, max: 10, step: 1, hint: 'Number of decimal places to round to' }] },
  'numeric-normalize': { title: 'Normalize (Min-Max)', description: 'Scales numeric values to a 0-1 range. Formula: (x - min) / (max - min). Use when you need bounded values.', operation: 'numeric', params: { operation: 'normalize' }, options: [] },
  'numeric-standardize': { title: 'Standardize (Z-Score)', description: 'Centers values around 0 with unit variance. Formula: (x - mean) / std. Common for linear regression, SVM, and distance-based algorithms. Values outside -3 to 3 may indicate outliers.', operation: 'numeric', params: { operation: 'standardize' }, options: [] },
  'numeric-robust': { title: 'Robust Scaling', description: 'Scales using median and IQR instead of mean/std. Formula: (x - median) / IQR. More robust to outliers than Z-score standardization.', operation: 'numeric', params: { operation: 'robust_scale' }, options: [] },
  'numeric-outliers': { title: 'Handle Outliers', description: 'Detects and handles statistical outliers using the IQR method. Outliers are capped to the fence values.', operation: 'numeric', params: { operation: 'outliers' }, options: [] },
  // Dedupe
  'remove-duplicates': { title: 'Remove Duplicates', description: 'Removes duplicate rows from the dataset. By default, considers all columns to determine duplicates.', operation: 'remove-duplicates', params: {}, options: [{ key: 'keep', label: 'Keep', type: 'select', choices: [{ value: 'first', text: 'First occurrence' }, { value: 'last', text: 'Last occurrence' }], hint: 'Which duplicate to keep when multiple exist' }] },
  'fuzzy-dedupe': { title: 'Fuzzy Match', description: 'Finds similar values and either removes duplicates or merges them. Useful for catching near-duplicates with typos or case differences.', operation: 'fuzzy-dedupe', params: { threshold: 85, matching_type: 'standard', mode: 'delete' }, options: [{ key: 'matching_type', label: 'Algorithm', type: 'select', choices: [{ value: 'standard', text: 'Standard (SequenceMatcher)' }, { value: 'permutation', text: 'Permutation (word order insensitive)' }, { value: 'levenshtein', text: 'Levenshtein (edit distance)' }], hint: 'Standard for typos, Permutation for word swaps, Levenshtein for short strings' }, { key: 'threshold', label: 'Similarity threshold (%)', type: 'range', min: 50, max: 100, step: 5, hint: 'Higher = stricter matching. 100 = exact only. Recommended: 80-90.' }, { key: 'mode', label: 'Action', type: 'select', choices: [{ value: 'delete', text: 'Delete duplicates' }, { value: 'merge_first', text: 'Merge to first' }, { value: 'merge_most_frequent', text: 'Merge to most frequent' }], hint: 'Delete removes rows; Merge keeps all rows but updates values' }] },
}

function showOpConfirmModal(opId) {
  const config = OP_CONFIGS[opId]
  if (!config) {
    toast.warning(`Unknown operation: ${opId}`)
    return
  }
  if (!effectiveSelectedColumns.value.length && !['remove-duplicates', 'fillna-drop'].includes(config.operation)) {
    toast.warning('Select column(s) first')
    return
  }
  opConfirmConfig.value = {
    title: config.title,
    description: config.description,
    operation: config.operation,
    params: { ...config.params },
    options: config.options,
    handler: opId,
  }
  showOpConfirm.value = true
}

async function onOpConfirmApply(params) {
  const config = opConfirmConfig.value
  const opId = config.handler
  showOpConfirm.value = false
  operating.value = true

  try {
    // Build the request based on operation type
    let endpoint, body
    const mergedParams = { ...OP_CONFIGS[opId]?.params, ...params }

    if (config.operation === 'fillna') {
      endpoint = `${apiUrl}/api/datasets/${datasetId.value}/operations/fillna`
      body = { columns: effectiveSelectedColumns.value.length ? effectiveSelectedColumns.value : undefined, ...mergedParams, row_indices: operationRowScope.value === 'selected' ? selectedRowIndices.value : undefined }
    } else if (config.operation === 'remove-duplicates') {
      endpoint = `${apiUrl}/api/datasets/${datasetId.value}/operations/remove-duplicates`
      body = mergedParams
    } else if (config.operation === 'fuzzy-dedupe') {
      endpoint = `${apiUrl}/api/datasets/${datasetId.value}/operations/fuzzy-dedupe`
      body = { 
        column: effectiveSelectedColumns.value[0] || null, 
        threshold: (mergedParams.threshold || 85) / 100,
        matching_type: mergedParams.matching_type || 'standard',
        mode: mergedParams.mode || 'delete'
      }
    } else if (config.operation === 'string-operations') {
      endpoint = `${apiUrl}/api/datasets/${datasetId.value}/operations/string-operations`
      body = { columns: effectiveSelectedColumns.value, ...mergedParams, row_indices: operationRowScope.value === 'selected' ? selectedRowIndices.value : undefined }
    } else if (config.operation === 'datetime-operations') {
      endpoint = `${apiUrl}/api/datasets/${datasetId.value}/operations/datetime-operations`
      body = { columns: effectiveSelectedColumns.value, ...mergedParams, row_indices: operationRowScope.value === 'selected' ? selectedRowIndices.value : undefined }
    } else if (config.operation === 'numeric') {
      endpoint = `${apiUrl}/api/datasets/${datasetId.value}/operations/numeric`
      body = { columns: effectiveSelectedColumns.value, ...mergedParams, row_indices: operationRowScope.value === 'selected' ? selectedRowIndices.value : undefined }
    } else {
      toast.warning(`Unknown operation: ${config.operation}`)
      return
    }

    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(body)
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message || 'Operation applied')
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Operation failed')
    }
  } catch (e) {
    toast.error(e.message)
  } finally {
    operating.value = false
  }
}

async function applyRowFilter() {
  showRowFilterModal.value = false
  page.value = 1
  await refreshData()
}

function clearRowFilter() {
  rowFilters.value = {}
  columnFilterState.value = {}
  filteredMatchingIndices.value = null
  filteredTotalMatching.value = null
  showRowFilterModal.value = false
  page.value = 1
  refreshData()
}

function clearColumnFilters() {
  columnFilterState.value = {}
  page.value = 1
  refreshData()
}

async function fetchUniqueValuesForColumn(column) {
  if (fetchingUniqueValues.value[column]) return
  fetchingUniqueValues.value[column] = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/unique-values?column=${encodeURIComponent(column)}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      const data = await res.json()
      columnUniqueValues.value[column] = data.values || []
      columnUniqueCounts.value[column] = data.total_unique || 0
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed to load unique values')
    }
  } catch (e) {
    toast.error(e.message)
  } finally {
    fetchingUniqueValues.value[column] = false
  }
}

function onColumnFilterChanged({ column, selectedValues }) {
  if (selectedValues.length === 0) {
    delete columnFilterState.value[column]
  } else {
    columnFilterState.value[column] = selectedValues
  }
  // Trigger reactivity
  columnFilterState.value = { ...columnFilterState.value }
  page.value = 1
  refreshData()
}

function toggleRowSelection(pageIndex) {
  // Convert page-relative index to absolute dataset index
  const absoluteIndex = resolveAbsoluteRowIndex(pageIndex)
  const idx = selectedRowIndices.value.indexOf(absoluteIndex)
  if (idx >= 0) selectedRowIndices.value.splice(idx, 1)
  else selectedRowIndices.value.push(absoluteIndex)
}

function toggleAllRows() {
  if (selectedRowIndices.value.length === filteredData.value.length) {
    selectedRowIndices.value = []
  } else {
    selectedRowIndices.value = filteredData.value.map((_, i) => resolveAbsoluteRowIndex(i))
  }
}

async function deleteSelectedRows() {
  if (!selectedRowIndices.value.length) return
  const ok = await showConfirm({ title: 'Delete Selected', message: `Delete ${selectedRowIndices.value.length} selected row(s)?`, variant: 'danger', confirmText: 'Delete' })
  if (!ok) return
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/delete-rows`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ mode: 'visible', indices: selectedRowIndices.value })
    })
    if (res.ok) {
      toast.success(`${selectedRowIndices.value.length} row(s) deleted`)
      selectedRowIndices.value = []
      await refreshData()
    } else { const err = await res.json(); toast.error(err.detail || 'Delete failed') }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

function showPrompt(options) {
  return new Promise((resolve) => {
    promptResolve = resolve
    promptConfig.value = {
      show: true,
      title: options.title || 'Input',
      message: options.message || '',
      defaultValue: options.defaultValue || '',
      inputType: options.inputType || 'text',
      confirmText: options.confirmText || 'OK',
    }
  })
}

function onPromptConfirm(val) {
  promptConfig.value.show = false
  if (promptResolve) { promptResolve(val); promptResolve = null }
}

function onPromptCancel() {
  promptConfig.value.show = false
  if (promptResolve) { promptResolve(null); promptResolve = null }
}

function showConfirm(options) {
  return new Promise((resolve) => {
    confirmResolve = resolve
    confirmConfig.value = {
      show: true,
      title: options.title || 'Confirm',
      message: options.message || '',
      confirmText: options.confirmText || 'Confirm',
      variant: options.variant || 'primary',
    }
  })
}

function onConfirmOk() {
  confirmConfig.value.show = false
  if (confirmResolve) { confirmResolve(true); confirmResolve = null }
}

function onConfirmCancel() {
  confirmConfig.value.show = false
  if (confirmResolve) { confirmResolve(false); confirmResolve = null }
}

async function deleteRows(mode) {
  let n
  if (mode === 'first') {
    const val = await showPrompt({ title: 'Delete First N Rows', message: 'Delete first N rows:', defaultValue: '1', inputType: 'number' })
    if (!val) return
    n = parseInt(val)
    if (isNaN(n) || n < 1) return
    if (!(await showConfirm({ title: 'Delete Rows', message: `Delete first ${n} row(s)?`, variant: 'danger', confirmText: 'Delete' }))) return
  } else if (mode === 'last') {
    const val = await showPrompt({ title: 'Delete Last N Rows', message: 'Delete last N rows:', defaultValue: '1', inputType: 'number' })
    if (!val) return
    n = parseInt(val)
    if (isNaN(n) || n < 1) return
    if (!(await showConfirm({ title: 'Delete Rows', message: `Delete last ${n} row(s)?`, variant: 'danger', confirmText: 'Delete' }))) return
  } else if (mode === 'range') {
    const val1 = await showPrompt({ title: 'Delete Row Range', message: 'Delete from row number:', defaultValue: '1', inputType: 'number' })
    if (!val1) return
    const n1 = parseInt(val1)
    if (isNaN(n1) || n1 < 1) return
    const val2 = await showPrompt({ title: 'Delete Row Range', message: `Delete up to row number (inclusive):`, defaultValue: `${n1}`, inputType: 'number' })
    if (!val2) return
    const n2 = parseInt(val2)
    if (isNaN(n2) || n2 < n1) return
    n = n1
    const count = n2 - n1 + 1
    if (!(await showConfirm({ title: 'Delete Rows', message: `Delete rows ${n1} to ${n2} (${count} rows)?`, variant: 'danger', confirmText: 'Delete' }))) return
    // Send n1 and count to backend
    operating.value = true
    try {
      const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/delete-rows`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({ mode: 'range', start: n1 - 1, end: n2 })
      })
      if (res.ok) { toast.success('Rows deleted'); await refreshData() }
      else { const err = await res.json(); toast.error(err.detail || 'Delete failed') }
    } catch (e) { toast.error(e.message) }
    finally { operating.value = false }
    return
  }
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/delete-rows`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ mode, count: n })
    })
    if (res.ok) { toast.success('Rows deleted'); await refreshData() }
    else { const err = await res.json(); toast.error(err.detail || 'Delete failed') }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

async function deleteVisibleRows() {
  if (!filteredData.value.length) { toast.warning('No visible rows to delete'); return }
  const count = filteredTotalMatching.value || filteredData.value.length
  if (!(await showConfirm({ title: 'Delete Rows', message: `Delete ${count} row(s)${hasActiveFilter.value ? ' matching filter' : ''}?`, variant: 'danger', confirmText: 'Delete' }))) return
  operating.value = true
  try {
    let body
    if (filteredMatchingIndices.value) {
      // Server-side filter: use matching indices from the filtered response
      body = { mode: 'visible', indices: filteredMatchingIndices.value }
    } else {
      // No filter: use current page indices
      body = { mode: 'visible', indices: filteredData.value.map((_, i) => i) }
    }
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/delete-rows`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(body)
    })
    if (res.ok) { toast.success('Rows deleted'); rowFilters.value = {}; filteredMatchingIndices.value = null; await refreshData() }
    else { const err = await res.json(); toast.error(err.detail || 'Delete failed') }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

async function undo() {
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/undo`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) { toast.success('Undo successful'); await refreshData() }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

const canMoveLeft = computed(() => {
  if (!selectedColumns.value.length) return false
  const allCols = columns.value.map(c => c.field)
  return selectedColumns.value.some(c => allCols.indexOf(c) > 0)
})

const canMoveRight = computed(() => {
  if (!selectedColumns.value.length) return false
  const allCols = columns.value.map(c => c.field)
  return selectedColumns.value.some(c => allCols.indexOf(c) < allCols.length - 1)
})

async function reorderColumns(direction) {
  if (!selectedColumns.value.length) return
  const allCols = columns.value.map(c => c.field)
  const selected = selectedColumns.value
  const newOrder = [...allCols]

  if (direction === 'left') {
    // Process left to right so each swap moves a selected column left by 1
    for (let i = 1; i < newOrder.length; i++) {
      if (selected.includes(newOrder[i]) && !selected.includes(newOrder[i - 1])) {
        [newOrder[i - 1], newOrder[i]] = [newOrder[i], newOrder[i - 1]]
      }
    }
  } else {
    // Process right to left so each swap moves a selected column right by 1
    for (let i = newOrder.length - 2; i >= 0; i--) {
      if (selected.includes(newOrder[i]) && !selected.includes(newOrder[i + 1])) {
        [newOrder[i], newOrder[i + 1]] = [newOrder[i + 1], newOrder[i]]
      }
    }
  }

  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/reorder-columns`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ columns: newOrder })
    })
    if (res.ok) {
      toast.success('Columns reordered')
      selectedColumns.value = []
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Reorder failed')
    }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

async function applyColumnReorder(newOrder) {
  if (!newOrder || newOrder.length === 0) return
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/reorder-columns`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ columns: newOrder })
    })
    if (res.ok) {
      toast.success('Columns reordered')
      selectedColumns.value = []
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Reorder failed')
    }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

const canMoveRowUp = computed(() => {
  if (!selectedRowIndices.value.length) return false
  const allIndices = selectedRowIndices.value
  const currentPageOffset = (page.value - 1) * limit.value
  // Can move up if any selected row is not the first row of the dataset
  return allIndices.some(i => i > 0)
})

const canMoveRowDown = computed(() => {
  if (!selectedRowIndices.value.length) return false
  // Can move down if any selected row is not the last row
  return selectedRowIndices.value.some(i => i < totalRows.value - 1)
})

const completedOpsCount = computed(() => operations.value.filter(op => !op.is_undone).length)

const canParseImport = computed(() => {
  if (importMode.value === 'paste') return importText.value.trim().length > 0
  return importFile.value !== null
})

const allImportSelected = computed(() =>
  importPreview.value && importPreview.value.length > 0 &&
  importPreview.value.filter(o => !o.column_missing).every(o => o.selected)
)
const someImportSelected = computed(() =>
  importPreview.value && importPreview.value.some(o => o.selected)
)

function toggleAllImport() {
  if (!importPreview.value) return
  const allSel = allImportSelected.value
  importPreview.value.forEach(o => {
    if (!o.column_missing) o.selected = !allSel
  })
}

async function exportOperations() {
  const recipe = operations.value
    .filter(op => !op.is_undone)
    .map(op => ({
      operation: op.operation_type,
      column: op.operation_params?.column || null,
      columns: op.operation_params?.columns || null,
      params: op.operation_params || {},
    }))

  const json = JSON.stringify(recipe, null, 2)
  const baseName = `operations-recipe-${datasetId.value.slice(0, 8)}`

  try {
    if (exportZip.value) {
      // Gzip compress using CompressionStream API
      const cs = new CompressionStream('gzip')
      const writer = cs.writable.getWriter()
      writer.write(new TextEncoder().encode(json))
      writer.close()
      const compressed = await new Response(cs.readable).blob()
      const url = URL.createObjectURL(compressed)
      const a = document.createElement('a')
      a.href = url
      a.download = `${baseName}.json.gz`
      a.click()
      URL.revokeObjectURL(url)
      toast.success('Recipe exported (gzipped)')
    } else {
      const blob = new Blob([json], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${baseName}.json`
      a.click()
      URL.revokeObjectURL(url)
      toast.success('Recipe exported')
    }
  } catch (e) {
    // Fallback if CompressionStream is not supported
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${baseName}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.warning('Compression not supported, exported as plain JSON')
  }

  showExportRecipe.value = false
  exportZip.value = false
}

async function onImportFileSelected() {
  importError.value = ''
  if (!importFile.value) return
  try {
    const text = await importFile.value.text()
    importText.value = text
  } catch (e) {
    importError.value = 'Failed to read file: ' + e.message
  }
}

function parseImport() {
  importError.value = ''
  let raw = importText.value.trim()
  if (!raw) { importError.value = 'No data to import'; return }

  let operations
  try {
    operations = JSON.parse(raw)
  } catch (e) {
    importError.value = 'Invalid JSON: ' + e.message
    return
  }

  if (!Array.isArray(operations)) {
    importError.value = 'Expected a JSON array of operations'
    return
  }

  if (operations.length === 0) {
    importError.value = 'No operations found in the JSON'
    return
  }

  const existingCols = columns.value.map(c => c.field)
  importPreview.value = operations.map((op, i) => {
    const opColumn = op.column || op.params?.column
    const opColumns = op.columns || op.params?.columns
    let columnMissing = false
    if (opColumn && !existingCols.includes(opColumn)) columnMissing = true
    if (opColumns && opColumns.some(c => !existingCols.includes(c))) columnMissing = true
    return {
      operation: op.operation,
      column: opColumn,
      columns: opColumns,
      params: op.params || {},
      selected: !columnMissing,
      column_missing: columnMissing,
    }
  })
}

async function applyImportedRecipe() {
  if (!importPreview.value) return
  const ops = importPreview.value.filter(o => o.selected).map(o => ({
    operation: o.operation,
    column: o.column,
    columns: o.columns,
    params: o.params,
  }))

  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/import-recipe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ operations: ops })
    })
    if (res.ok) {
      importResults.value = await res.json()
      await refreshData()
    } else {
      const err = await res.json()
      importError.value = err.detail || 'Import failed'
      importPreview.value = null
    }
  } catch (e) {
    importError.value = e.message
    importPreview.value = null
  } finally {
    operating.value = false
  }
}

function closeImportModal() {
  showImportRecipe.value = false
  importPreview.value = null
  importResults.value = null
  importText.value = ''
  importFile.value = null
  importError.value = ''
}

const canAddRecords = computed(() => {
  if (addMode.value === 'single') {
    return pendingRows.value.length > 0 || Object.values(singleRow.value).some(v => v !== undefined && v !== '')
  }
  if (addMode.value === 'csv') return csvText.value.trim().length > 0
  if (addMode.value === 'json') return jsonText.value.trim().length > 0
  return false
})

function addAnotherRow() {
  const row = { ...singleRow.value }
  // Only add if at least one field has a value
  if (Object.values(row).some(v => v !== undefined && v !== '')) {
    pendingRows.value.push(row)
  }
  singleRow.value = {}
}

async function submitAddRecords() {
  let body = {}
  if (addMode.value === 'single') {
    // Collect the current row too
    const row = { ...singleRow.value }
    if (Object.values(row).some(v => v !== undefined && v !== '')) {
      pendingRows.value.push(row)
    }
    if (!pendingRows.value.length) {
      toast.warning('Add at least one row')
      return
    }
    body = { records: pendingRows.value }
  } else if (addMode.value === 'csv') {
    if (!csvText.value.trim()) { toast.warning('Paste CSV data'); return }
    body = { csv_text: csvText.value }
  } else if (addMode.value === 'json') {
    if (!jsonText.value.trim()) { toast.warning('Paste JSON data'); return }
    let records
    try {
      records = JSON.parse(jsonText.value)
    } catch {
      toast.error('Invalid JSON format')
      return
    }
    if (!Array.isArray(records)) { toast.error('JSON must be an array of objects'); return }
    body = { records }
  }

  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/add-records`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(body)
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message || 'Records added')
      showAddRecords.value = false
      singleRow.value = {}
      pendingRows.value = []
      csvText.value = ''
      jsonText.value = ''
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed to add records')
    }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

async function reorderRows(direction) {
  if (!selectedRowIndices.value.length) return
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/reorder-rows`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ indices: selectedRowIndices.value, direction })
    })
    if (res.ok) {
      toast.success('Rows reordered')
      selectedRowIndices.value = []
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Reorder failed')
    }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

async function redo(opId = null) {
  operating.value = true
  try {
    const body = opId ? { operation_id: opId } : {}
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/redo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(body)
    })
    if (res.ok) { toast.success('Redo successful'); await refreshData() }
    else {
      const err = await res.json()
      toast.error(err.detail || 'Failed to redo')
    }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

async function applyStructuralAiClean(payload) {
  if (!effectiveSelectedColumns.value || effectiveSelectedColumns.value.length === 0) {
    toast.warning('No column selected'); return
  }
  if (!payload.instruction) return
  if (!payload.agentId) {
    toast.warning('Please select an AI Agent'); return
  }
  const body = {
    columns: effectiveSelectedColumns.value,
    instruction: payload.instruction,
    type: 'structural',
    agent_id: payload.agentId,
    system_prompt: payload.systemPrompt,
    user_prompt: payload.userPrompt,
    rows_for_context: payload.rowsForContext,
    include_description: payload.includeDescription
  };
  operating.value = true;
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/ai-clean`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify(body)
    });
    if (res.ok) {
      toast.success('AI structural cleaning applied');
      showStructuralAiModal.value = false;
      selectedColumns.value = [];
      await refreshData()
    }
    else {
      const err = await res.json();
      toast.error(err.detail || 'AI structural cleaning failed')
    }
  } catch (e) {
    toast.error(e.message)
  }
  finally {
    operating.value = false;
  }
}

function closeDataAiModal() {
  showDataAiModal.value = false
  batchProgress.value = null
  operating.value = false
}

async function onFuzzyMatchApply(payload) {
  if (!payload.column) { toast.warning('Select a column first'); return }
  if (!payload.mapping || Object.keys(payload.mapping).length === 0) { toast.warning('No value mapping defined'); return }

  
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/fuzzy-advanced`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({
        column: payload.column,
        mapping: payload.mapping,
        matching_type: payload.matching_type || 'standard',
        threshold: (payload.threshold || 85) / 100
      })
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message || 'Fuzzy match applied')
      showFuzzyMatchModal.value = false
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Fuzzy match failed')
    }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

function onFuzzyAiHelp(payload) {
  // Open the AI modal with pre-filled context for fuzzy matching
  fuzzyAiContext.value = {
    column: payload.column,
    uniqueValues: payload.uniqueValues,
    clusters: payload.clusters,
    mode: payload.mode
  }
  showDataAiModal.value = true
}

async function applyDataAiClean(payload) {
  if (!effectiveSelectedColumns.value || effectiveSelectedColumns.value.length === 0) {
    toast.warning('No column selected'); return
  }
  if (!payload.instruction) { toast.warning('Enter an instruction'); return }
  if (!payload.agentId) { toast.warning('Please select an AI Agent'); return }

  if (!payload.batchProcessAll) {
    // Single batch mode (original behavior)
    const body = {
      columns: effectiveSelectedColumns.value,
      instruction: payload.instruction,
      type: 'data',
      agent_id: payload.agentId,
      batch_size: 10,
      system_prompt: payload.systemPrompt,
      user_prompt: payload.userPrompt,
      rows_for_context: payload.rowsForContext,
      include_description: payload.includeDescription
    }
    operating.value = true
    try {
      const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/ai-clean`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify(body)
      })
      if (res.ok) {
        toast.success('AI data cleaning applied')
        showDataAiModal.value = false
        selectedColumns.value = []
        await refreshData()
      } else {
        const err = await res.json()
        toast.error(err.detail || 'AI data cleaning failed')
      }
    } catch (e) { toast.error(e.message) }
    finally { operating.value = false }
    return
  }

  // Batch mode: start job then stream via SSE
  operating.value = true
  batchProgress.value = { status: 'running', total: 0, completed: 0, failed: 0, percentage: 0 }

  try {
    // Step 1: Create job
    const startRes = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/ai-batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({
        columns: effectiveSelectedColumns.value,
        instruction: payload.instruction,
        type: 'data',
        agent_id: payload.agentId,
        batch_size: payload.batchSize,
        delay: payload.batchDelay,
        start_row: payload.batchStartRow,
        process_all: true,
        system_prompt: payload.systemPrompt,
        user_prompt: payload.userPrompt,
        rows_for_context: payload.rowsForContext,
        include_description: payload.includeDescription
      })
    })

    if (!startRes.ok) {
      const err = await startRes.json()
      toast.error(err.detail || 'Failed to start batch job')
      operating.value = false
      return
    }

    const { job_id, warning } = await startRes.json()
    if (warning) toast.warning(warning)

    // Step 2: Stream progress via SSE using fetch (EventSource can't send headers)
    const columnsParam = effectiveSelectedColumns.value.join(',')
    const sseUrl = `${apiUrl}/api/datasets/${datasetId.value}/ai-batch/${job_id}/stream?columns=${encodeURIComponent(columnsParam)}&instruction=${encodeURIComponent(payload.instruction)}&agent_id=${payload.agentId}&batch_size=${payload.batchSize}&delay=${payload.batchDelay}&start_row=${payload.batchStartRow}`

    try {
      const sseRes = await fetch(sseUrl, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      if (!sseRes.ok) {
        const err = await sseRes.json().catch(() => ({}))
        toast.error(err.detail || `SSE connection failed (${sseRes.status})`)
        operating.value = false
        return
      }

      const reader = sseRes.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        // Parse SSE events from buffer
        const events = buffer.split('\n\n')
        buffer = events.pop() || '' // keep incomplete event in buffer

        for (const evt of events) {
          const lines = evt.split('\n')
          let eventType = ''
          let data = ''
          for (const line of lines) {
            if (line.startsWith('event: ')) eventType = line.slice(7)
            if (line.startsWith('data: ')) data = line.slice(6)
          }
          if (!eventType || !data) continue

          const parsed = JSON.parse(data)

          if (eventType === 'progress') {
            batchProgress.value = parsed
          } else if (eventType === 'done') {
            batchProgress.value = parsed
            toast.success(`Batch complete: ${parsed.completed} succeeded, ${parsed.failed} failed`)
            await refreshData()
          } else if (eventType === 'error') {
            batchProgress.value = parsed
            toast.error('Batch processing failed')
          }
        }
      }
    } catch (e) {
      toast.error(e.message || 'SSE connection lost')
    } finally {
      operating.value = false
    }

  } catch (e) {
    toast.error(e.message)
    operating.value = false
  }
}

async function pasteFromClipboard() {
  try {
    const text = await navigator.clipboard.readText()
    clipboardData.value = text
    toast.success('Pasted from clipboard')
  } catch (e) { 
    toast.error('Failed to paste: ' + e.message + '. Make sure you are using HTTPS.') 
  }
}

async function importFromClipboard() {
  if (!clipboardData.value.trim()) return
  operating.value = true
  try {
    const blob = new Blob([clipboardData.value], { type: 'text/csv' })
    const file = new File([blob], 'clipboard.csv', { type: 'text/csv' })
    const formData = new FormData()
    formData.append('file', file)
    formData.append('project_id', route.params.id)
    if (clipboardDatasetName.value) formData.append('name', clipboardDatasetName.value)
    
    const res = await fetch(`${apiUrl}/api/datasets/import`, {
      method: 'POST',
      body: formData,
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) { toast.success('Data imported successfully'); showClipboardImport.value = false; clipboardData.value = ''; await refreshData() }
    else throw new Error('Import failed')
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

async function copyToClipboard() {
  if (!data.value || data.value.length === 0) { toast.warning('No data to copy'); return }
  try {
    const headers = Object.keys(data.value[0])
    const csvRows = [headers.join(','), ...data.value.map(row => headers.map(h => {
      const val = row[h]
      if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) return `"${val.replace(/"/g, '""')}"`
      return val ?? ''
    }).join(','))]
    await navigator.clipboard.writeText(csvRows.join('\n'))
    toast.success('Data copied to clipboard')
  } catch (e) { toast.error('Failed to copy: ' + e.message + '. Make sure you are using HTTPS.') }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function formatOperationParams(params) {
  if (!params) return ''
  try {
    const p = typeof params === 'string' ? JSON.parse(params) : params
    const parts = []
    if (p.column) parts.push(`column: ${p.column}`)
    if (p.columns) parts.push(`columns: ${p.columns.join(', ')}`)
    if (p.operation) parts.push(`op: ${p.operation}`)
    if (p.method) parts.push(`method: ${p.method}`)
    if (p.new_name) parts.push(`→ ${p.new_name}`)
    return parts.join(' | ')
  } catch {
    return ''
  }
}

async function undoOperation(opId) {
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/undo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ operation_id: opId })
    })
    if (res.ok) {
      toast.success('Operation undone')
      selectedOpIds.value = selectedOpIds.value.filter(id => id !== opId)
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed to undo')
    }
  } catch (e) {
    toast.error(e.message)
  } finally {
    operating.value = false
  }
}

async function redoOperation(opId) {
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/redo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ operation_id: opId })
    })
    if (res.ok) {
      toast.success('Operation redone')
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed to redo')
    }
  } catch (e) {
    toast.error(e.message)
  } finally {
    operating.value = false
  }
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

async function deleteOperation(opId) {
  if (!(await showConfirm({ title: 'Delete Operation', message: 'Delete this operation record?', variant: 'danger', confirmText: 'Delete' }))) return
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/${opId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) {
      toast.success('Operation deleted')
      await fetchOperations()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed to delete')
    }
  } catch (e) { toast.error(e.message) }
  finally { operating.value = false }
}

function toggleOpSelection(opId) {
  const idx = selectedOpIds.value.indexOf(opId)
  if (idx >= 0) selectedOpIds.value.splice(idx, 1)
  else selectedOpIds.value.push(opId)
}

function toggleAllOps() {
  if (allOpsSelected.value) {
    selectedOpIds.value = []
  } else {
    selectedOpIds.value = operations.value.map(op => op.id)
  }
}

async function undoSelectedOps() {
  if (!selectedOpIds.value.length) return
  // Only undo operations that are not already undone
  const undoable = selectedOpIds.value.filter(id => {
    const op = operations.value.find(o => o.id === id)
    return op && !op.is_undone
  })
  if (!undoable.length) {
    toast.warning('No operations to undo.')
    return
  }
  if (!(await showConfirm({ title: 'Undo Operations', message: `Undo ${undoable.length} operation(s)?`, variant: 'warning', confirmText: 'Undo' }))) return
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/undo-batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ operation_ids: undoable })
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message)
      selectedOpIds.value = []
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed to undo')
    }
  } catch (e) {
    toast.error(e.message)
  } finally {
    operating.value = false
  }
}

async function redoSelectedOps() {
  if (!selectedOpIds.value.length) return
  // Only redo operations that are already undone
  const redoable = selectedOpIds.value.filter(id => {
    const op = operations.value.find(o => o.id === id)
    return op && op.is_undone
  })
  if (!redoable.length) {
    toast.warning('No operations to redo.')
    return
  }
  if (!(await showConfirm({ title: 'Redo Operations', message: `Redo ${redoable.length} operation(s)?`, variant: 'success', confirmText: 'Redo' }))) return
  operating.value = true
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/redo-batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ operation_ids: redoable })
    })
    if (res.ok) {
      const data = await res.json()
      toast.success(data.message)
      selectedOpIds.value = []
      await refreshData()
    } else {
      const err = await res.json()
      toast.error(err.detail || 'Failed to redo')
    }
  } catch (e) {
    toast.error(e.message)
  } finally {
    operating.value = false
  }
}

async function deleteSelectedOps() {
  if (!selectedOpIds.value.length) return
  // Only undone operations can be deleted (backend enforces this)
  const deletable = selectedOpIds.value.filter(id => {
    const op = operations.value.find(o => o.id === id)
    return op && op.is_undone
  })
  if (!deletable.length) {
    toast.warning('No undone operations to delete.')
    return
  }
  if (!(await showConfirm({ title: 'Delete Operations', message: `Permanently delete ${deletable.length} undone operation record(s)?`, variant: 'danger', confirmText: 'Delete' }))) return
  operating.value = true
  let deleted = 0
  try {
    for (const opId of deletable) {
      const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations/${opId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      if (res.ok) deleted++
    }
    if (deleted > 0) toast.success(`${deleted} operation record(s) deleted`)
    selectedOpIds.value = []
    await fetchOperations()
  } catch (e) {
    toast.error(e.message)
  } finally {
    operating.value = false
  }
}

async function fetchOperations() {
  try {
    const res = await fetch(`${apiUrl}/api/datasets/${datasetId.value}/operations`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) { const d = await res.json(); operations.value = d.operations || d || []; selectedOpIds.value = [] }
  } catch { /* silent */ }
}
</script>

<style scoped>
.data-viewer {
   background: #f8f9fa;
   min-height: 100vh;
}
.history-sidebar {
   position: fixed;
   top: 0;
   right: 0;
   width: 360px;
   height: 100vh;
   background: #f8fafc;
   box-shadow: -4px 0 16px rgba(0,0,0,0.08);
   z-index: 99999 !important;
   overflow-y: auto;
   padding: 70px 12px 12px;
}

.history-sidebar h6 {
   font-size: 0.85rem;
   font-weight: 600;
   color: #334155;
}

.history-sidebar .card {
   border-radius: 8px;
   border: 1px solid #e2e8f0;
   transition: box-shadow 0.15s ease;
}

.history-sidebar .card:hover {
   box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.history-sidebar .card-body {
   padding: 10px 12px;
}

.history-sidebar .badge {
   font-size: 0.7rem;
   font-weight: 500;
}

/* Column Visibility Dropdown */
.column-visibility-dropdown .dropdown-menu {
  max-height: 300px;
  overflow-y: auto;
  min-width: 180px;
}
</style>
