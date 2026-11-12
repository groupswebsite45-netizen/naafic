<script setup lang="ts">
import { ref, reactive } from 'vue';
import { superAdminService } from '../../../services/superAdminService';
import { Institution } from '../../../types/institution';

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'created', institution: Institution): void;
}>();

const isSubmitting = ref(false);
const errorMessage = ref('');

const logoFileInput = ref<HTMLInputElement | null>(null);
const logoPreview = ref<string | null>(null);
const selectedLogoFile = ref<File | null>(null);

function handleLogoFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  if (file.size > 5 * 1024 * 1024) {
    errorMessage.value = 'Logo file size exceeds 5MB limit.';
    return;
  }

  selectedLogoFile.value = file;
  logoPreview.value = URL.createObjectURL(file);
}

function clearLogo() {
  selectedLogoFile.value = null;
  logoPreview.value = null;
  formData.logo_url = '';
  if (logoFileInput.value) {
    logoFileInput.value.value = '';
  }
}

const formData = reactive({
  name: '',
  type: 'Primary & Secondary School',
  logo_url: '',
  contact_person: '',
  email: '',
  phone: '+252 61 ',
  region: 'Banaadir',
  city: 'Mogadishu',
  address: '',
  subscription_plan: 'Professional School',
  subscription_start_date: new Date().toISOString().split('T')[0],
  subscription_expiry_date: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString().split('T')[0],
  status: 'ACTIVE',
  // Initial Admin User
  create_admin: true,
  admin_full_name: '',
  admin_email: '',
  admin_username: '',
  admin_password: '',
  admin_phone: '+252 61 ',
});

const institutionTypes = [
  'Primary School',
  'Secondary School',
  'Primary & Secondary School',
  'Academy',
  'College',
  'Institute',
  'Other',
];

const subscriptionPlans = [
  'Starter Academy',
  'Professional School',
  'Enterprise Institution',
];

const regions = [
  'Banaadir',
  'Galgaduud',
  'Mudug',
  'Bari',
  'Nugaal',
  'Lower Juba',
  'Bay',
  'Bakool',
  'Hiran',
  'Awdal',
  'Woqooyi Galbeed',
];

async function handleSubmit() {
  errorMessage.value = '';

  if (!formData.name.trim()) {
    errorMessage.value = 'Institution name is required.';
    return;
  }

  if (formData.create_admin) {
    if (!formData.admin_full_name || !formData.admin_email || !formData.admin_username || !formData.admin_password) {
      errorMessage.value = 'Please provide complete administrator details.';
      return;
    }
    if (formData.admin_password.length < 8) {
      errorMessage.value = 'Administrator password must be at least 8 characters.';
      return;
    }
  }

  isSubmitting.value = true;
  try {
    if (selectedLogoFile.value) {
      try {
        const uploadRes = await superAdminService.uploadLogo(selectedLogoFile.value);
        formData.logo_url = uploadRes.url;
      } catch (uploadErr: any) {
        errorMessage.value = 'Failed to upload institution logo file: ' + (uploadErr.response?.data?.detail || uploadErr.message);
        isSubmitting.value = false;
        return;
      }
    }

    const payload: any = {
      name: formData.name.trim(),
      type: formData.type,
      logo_url: formData.logo_url ? formData.logo_url.trim() : null,
      contact_person: formData.contact_person ? formData.contact_person.trim() : null,
      email: formData.email ? formData.email.trim() : null,
      phone: formData.phone ? formData.phone.trim() : null,
      region: formData.region,
      city: formData.city ? formData.city.trim() : null,
      address: formData.address ? formData.address.trim() : null,
      subscription_plan: formData.subscription_plan,
      subscription_start_date: formData.subscription_start_date,
      subscription_expiry_date: formData.subscription_expiry_date,
      status: formData.status,
    };

    if (formData.create_admin) {
      payload.admin_account = {
        full_name: formData.admin_full_name.trim(),
        email: formData.admin_email.trim(),
        username: formData.admin_username.trim(),
        password: formData.admin_password,
        phone_number: formData.admin_phone ? formData.admin_phone.trim() : null,
      };
    }

    const created = await superAdminService.registerInstitution(payload);
    emit('created', created);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || err.message || 'Failed to register institution. Please try again.';
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="rim-backdrop" @click.self="emit('close')">
    <div class="rim-modal">
      <!-- Modal Header -->
      <div class="rim-header">
        <div class="flex items-center gap-3">
          <div class="rim-emblem-box">
            <svg class="w-6 h-6" viewBox="0 0 36 40" fill="none">
              <path d="M18 2L4 7V18C4 28 10 36 18 39C26 36 32 28 32 18V7L18 2Z" fill="#0A2558" stroke="#1E40AF" stroke-width="1.5"/>
              <path d="M22.5 12C20.5 10.8 17.5 10.5 15 11.8C13 12.8 12 14.5 12 16.5C12 20 23.5 19 23.5 24C23.5 27.5 19.5 29 16 28C13.5 27.2 12 25.5 11.5 24.5" stroke="#FF6500" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <h2 class="rim-title">Register New Institution</h2>
            <p class="rim-subtitle">Onboard a school, academy, or college into Somroyal Technology Solutions.</p>
          </div>
        </div>
        <button class="rim-close-btn" @click="emit('close')" aria-label="Close modal">✕</button>
      </div>

      <!-- Alert Error -->
      <div v-if="errorMessage" class="rim-error-alert">
        <svg class="w-5 h-5 text-red-500 mr-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ errorMessage }}</span>
      </div>

      <!-- Form Body -->
      <form @submit.prevent="handleSubmit" class="rim-form">
        <!-- Section 1: Institution Details -->
        <div class="rim-section-header">
          <span class="rim-section-number">1</span>
          <h3 class="rim-section-title">Institution Profile</h3>
        </div>

        <div class="rim-grid rim-grid-2">
          <div class="rim-field">
            <label class="rim-label">Institution Name <span class="text-red-500">*</span></label>
            <input
              v-model="formData.name"
              type="text"
              class="rim-input"
              placeholder="e.g. Mogadishu Elite Academy"
              required
            />
          </div>

          <div class="rim-field">
            <label class="rim-label">Institution Type <span class="text-red-500">*</span></label>
            <select v-model="formData.type" class="rim-select" required>
              <option v-for="t in institutionTypes" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>
        </div>

        <!-- School Logo Upload & URL Field -->
        <div class="rim-field mb-3">
          <label class="rim-label">School Logo / Emblem</label>
          <div class="flex items-center gap-3.5 p-3 rounded-xl border border-slate-200 bg-slate-50/70">
            <div class="w-14 h-14 rounded-lg bg-white border border-slate-200 flex items-center justify-center overflow-hidden flex-shrink-0 shadow-sm">
              <img
                v-if="logoPreview || formData.logo_url"
                :src="logoPreview || formData.logo_url"
                alt="Logo Preview"
                class="w-full h-full object-contain p-1"
              />
              <svg v-else class="w-7 h-7 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="flex-1 flex flex-col gap-1.5">
              <div class="flex items-center gap-2">
                <input
                  type="file"
                  ref="logoFileInput"
                  accept="image/png, image/jpeg, image/svg+xml, image/webp"
                  class="hidden"
                  @change="handleLogoFileChange"
                />
                <button
                  type="button"
                  class="px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-100 shadow-sm transition"
                  @click="logoFileInput?.click()"
                >
                  Choose Logo Image (PNG, JPG, SVG, WebP)
                </button>
                <button
                  v-if="logoPreview || formData.logo_url"
                  type="button"
                  class="px-2.5 py-1.5 rounded-lg text-xs font-semibold text-red-600 hover:bg-red-50 transition"
                  @click="clearLogo"
                >
                  Clear
                </button>
              </div>
              <input
                v-model="formData.logo_url"
                type="text"
                class="rim-input text-xs"
                placeholder="Or paste external logo image URL (optional)"
              />
            </div>
          </div>
        </div>

        <div class="rim-grid rim-grid-3">
          <div class="rim-field">
            <label class="rim-label">Contact Person</label>
            <input
              v-model="formData.contact_person"
              type="text"
              class="rim-input"
              placeholder="e.g. Dr. Abdullahi Warsame"
            />
          </div>

          <div class="rim-field">
            <label class="rim-label">Official Email</label>
            <input
              v-model="formData.email"
              type="email"
              class="rim-input"
              placeholder="contact@institution.edu.so"
            />
          </div>

          <div class="rim-field">
            <label class="rim-label">Official Phone</label>
            <input
              v-model="formData.phone"
              type="tel"
              class="rim-input"
              placeholder="+252 61 0000000"
            />
          </div>
        </div>

        <div class="rim-grid rim-grid-3">
          <div class="rim-field">
            <label class="rim-label">Region / State <span class="text-red-500">*</span></label>
            <select v-model="formData.region" class="rim-select" required>
              <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>

          <div class="rim-field">
            <label class="rim-label">City</label>
            <input
              v-model="formData.city"
              type="text"
              class="rim-input"
              placeholder="e.g. Mogadishu"
            />
          </div>

          <div class="rim-field">
            <label class="rim-label">Physical Address</label>
            <input
              v-model="formData.address"
              type="text"
              class="rim-input"
              placeholder="e.g. Maka Al Mukarama Rd"
            />
          </div>
        </div>

        <!-- Section 2: Subscription & Licensing -->
        <div class="rim-section-header">
          <span class="rim-section-number">2</span>
          <h3 class="rim-section-title">Subscription & Licensing Tier</h3>
        </div>

        <div class="rim-grid rim-grid-3">
          <div class="rim-field">
            <label class="rim-label">Licensing Plan <span class="text-red-500">*</span></label>
            <select v-model="formData.subscription_plan" class="rim-select" required>
              <option v-for="p in subscriptionPlans" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>

          <div class="rim-field">
            <label class="rim-label">License Start Date</label>
            <input
              v-model="formData.subscription_start_date"
              type="date"
              class="rim-input"
              required
            />
          </div>

          <div class="rim-field">
            <label class="rim-label">License Expiry Date</label>
            <input
              v-model="formData.subscription_expiry_date"
              type="date"
              class="rim-input"
              required
            />
          </div>
        </div>

        <!-- Section 3: Initial Administrator Account Setup -->
        <div class="rim-section-header">
          <span class="rim-section-number">3</span>
          <h3 class="rim-section-title">Initial Administrator Account</h3>
        </div>

        <div class="rim-checkbox-wrap">
          <label class="rim-checkbox-label">
            <input
              v-model="formData.create_admin"
              type="checkbox"
              class="rim-checkbox"
            />
            <span>Create initial School Administrator account for this tenant</span>
          </label>
        </div>

        <div v-if="formData.create_admin" class="rim-admin-box">
          <div class="rim-grid rim-grid-2">
            <div class="rim-field">
              <label class="rim-label">Administrator Full Name <span class="text-red-500">*</span></label>
              <input
                v-model="formData.admin_full_name"
                type="text"
                class="rim-input"
                placeholder="e.g. Ali Ahmed Mohamed"
                :required="formData.create_admin"
              />
            </div>

            <div class="rim-field">
              <label class="rim-label">Admin Email <span class="text-red-500">*</span></label>
              <input
                v-model="formData.admin_email"
                type="email"
                class="rim-input"
                placeholder="principal@institution.edu.so"
                :required="formData.create_admin"
              />
            </div>
          </div>

          <div class="rim-grid rim-grid-2">
            <div class="rim-field">
              <label class="rim-label">Username <span class="text-red-500">*</span></label>
              <input
                v-model="formData.admin_username"
                type="text"
                class="rim-input"
                placeholder="school.admin"
                :required="formData.create_admin"
              />
            </div>

            <div class="rim-field">
              <label class="rim-label">Temporary Password <span class="text-red-500">*</span></label>
              <input
                v-model="formData.admin_password"
                type="password"
                class="rim-input"
                placeholder="Min 8 characters"
                :required="formData.create_admin"
              />
            </div>
          </div>
        </div>

        <!-- Modal Footer Actions -->
        <div class="rim-footer">
          <button type="button" class="rim-btn-cancel" @click="emit('close')" :disabled="isSubmitting">
            Cancel
          </button>
          <button type="submit" class="rim-btn-submit" :disabled="isSubmitting">
            <span v-if="isSubmitting">Registering Institution...</span>
            <span v-else>Register Institution</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.rim-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(6, 23, 55, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
  backdrop-filter: blur(4px);
  overflow-y: auto;
}

.rim-modal {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: 780px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.rim-header {
  padding: 1.25rem 1.75rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8fafc;
}

.rim-emblem-box {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #061737;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.rim-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #061737;
  margin: 0;
}

.rim-subtitle {
  font-size: 0.8rem;
  color: #64748b;
  margin: 0.2rem 0 0;
}

.rim-close-btn {
  background: transparent;
  border: none;
  font-size: 1.25rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
}

.rim-close-btn:hover {
  color: #0f172a;
}

.rim-error-alert {
  margin: 1rem 1.75rem 0;
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  font-size: 0.85rem;
  color: #b91c1c;
  display: flex;
  align-items: center;
  font-weight: 600;
}

.rim-form {
  padding: 1.25rem 1.75rem 1.75rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.rim-section-header {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-top: 0.25rem;
}

.rim-section-number {
  width: 24px;
  height: 24px;
  background: #ff6500;
  color: #ffffff;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rim-section-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #061737;
  margin: 0;
}

.rim-grid {
  display: grid;
  gap: 1rem;
}

.rim-grid-2 {
  grid-template-columns: repeat(2, 1fr);
}

.rim-grid-3 {
  grid-template-columns: repeat(3, 1fr);
}

.rim-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.rim-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #334155;
}

.rim-input,
.rim-select {
  padding: 0.6rem 0.85rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  background: #ffffff;
  outline: none;
  transition: all 0.15s ease;
}

.rim-input:focus,
.rim-select:focus {
  border-color: #ff6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.12);
}

.rim-checkbox-wrap {
  margin: 0.25rem 0;
}

.rim-checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e293b;
  cursor: pointer;
}

.rim-checkbox {
  width: 17px;
  height: 17px;
  accent-color: #ff6500;
}

.rim-admin-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.rim-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
  margin-top: 0.5rem;
}

.rim-btn-cancel {
  padding: 0.6rem 1.25rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
  color: #475569;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.rim-btn-cancel:hover {
  background: #f1f5f9;
}

.rim-btn-submit {
  padding: 0.6rem 1.5rem;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #ff6500 0%, #ea580c 100%);
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(255, 101, 0, 0.35);
  transition: all 0.15s;
}

.rim-btn-submit:hover:not(:disabled) {
  background: #ea580c;
  transform: translateY(-1px);
}

.rim-btn-submit:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .rim-grid-2,
  .rim-grid-3 {
    grid-template-columns: 1fr;
  }

  .rim-header {
    padding: 1rem 1.25rem;
  }

  .rim-form {
    padding: 1rem 1.25rem;
  }
}
</style>
