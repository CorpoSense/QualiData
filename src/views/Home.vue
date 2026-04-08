<template>
  <div id="home-page">
    <!-- Hero Section -->
    <section class="hero-section position-relative overflow-hidden">
      <div class="container">
        <div class="row align-items-center min-vh-75">
          <div class="col-lg-6 mb-5 mb-lg-0 text-center text-lg-start z-2">
            <span class="badge rounded-pill mb-4 px-3 py-2" style="background: rgba(79, 70, 229, 0.1); color: var(--primary-color); border: 1px solid rgba(79, 70, 229, 0.2); font-weight: 600; letter-spacing: 0.5px;">
              <i class="bi bi-lightning-charge-fill text-warning me-1"></i> Blazing fast!
            </span>
            <h1 class="display-3 fw-bolder mb-4 lh-tight">
              Master Your Data with <br class="d-none d-lg-block">
              <span class="text-gradient">AI Precision</span>
            </h1>
            <p class="lead text-secondary mb-5 pe-lg-5 fs-5">
              The ultimate platform for cleaning, normalizing, and enriching your master data. Say goodbye to manual spreadsheets and hello to automated intelligence.
            </p>
            <div class="d-flex flex-column flex-sm-row justify-content-center justify-content-lg-start gap-3 mb-5">
              <BButton variant="primary" size="lg" class="rounded-pill px-5" @click="goToDashboard">
                Get Started Free
              </BButton>
              <BButton variant="light" size="lg" class="rounded-pill px-4 border shadow-sm" @click="watchDemo">
                <i class="bi bi-play-circle-fill text-primary me-2"></i> Watch Demo
              </BButton>
            </div>
            
            <div class="d-flex align-items-center justify-content-center justify-content-lg-start gap-3">
              <div class="d-flex">
                <img src="https://i.pravatar.cc/100?img=1" alt="User" class="rounded-circle border border-2 border-white" style="width: 40px; height: 40px; z-index: 3;">
                <img src="https://i.pravatar.cc/100?img=2" alt="User" class="rounded-circle border border-2 border-white ms-n2" style="width: 40px; height: 40px; z-index: 2;">
                <img src="https://i.pravatar.cc/100?img=3" alt="User" class="rounded-circle border border-2 border-white ms-n2" style="width: 40px; height: 40px; z-index: 1;">
                <div class="rounded-circle bg-light border border-2 border-white d-flex align-items-center justify-content-center fw-bold text-primary" style="width: 40px; height: 40px; z-index: 0; margin-left: -12px; font-size: 12px;">
                  +2k
                </div>
              </div>
              <div class="text-start">
                <div class="d-flex text-warning mb-1" style="font-size: 12px;">
                  <i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i>
                </div>
                <p class="small text-secondary mb-0 fw-medium">Joined by <strong>2,000+</strong> data engineers</p>
              </div>
            </div>
          </div>
          
          <div class="col-lg-6 position-relative z-1">
            <div class="position-absolute w-100 h-100 bg-gradient-primary rounded-circle blur-3xl opacity-25" style="filter: blur(80px); transform: translate(-10%, -10%);"></div>
            
            <!-- Code/UI Mockup -->
            <div class="mockup-window ms-lg-4 mt-5 mt-lg-0" style="background: #1e293b; border-radius: 20px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); border: 1px solid rgba(255, 255, 255, 0.1); overflow: hidden;">
              <div class="mockup-header" style="background: #0f172a; padding: 12px 20px; display: flex; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05);">
                <div class="mockup-dots d-flex">
                  <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; background: #ff5f56;"></span>
                  <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; background: #ffbd2e;"></span>
                  <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; background: #27c93f;"></span>
                </div>
                <div class="text-center w-100 text-secondary" style="font-size: 12px; margin-left: -40px;">master-data-cleanup.csv</div>
              </div>
              <div class="p-4">
                <div class="mb-3 text-secondary small">Processing raw input...</div>
                <div class="data-row before align-items-center" style="display: flex; gap: 10px; padding: 12px; border-radius: 8px; margin-bottom: 8px; font-family: monospace; font-size: 13px; background: rgba(255, 255, 255, 0.03); color: #94a3b8;">
                  <div class="col-3 text-truncate">Jhn Doe</div>
                  <div class="col-3 text-truncate">ny, usa</div>
                  <div class="col-4 text-truncate">invalid_email</div>
                  <div class="col-2 text-end text-danger"><i class="bi bi-x-circle"></i></div>
                </div>
                <div class="my-3 d-flex align-items-center gap-3">
                  <hr class="flex-grow-1 border-secondary opacity-25;">
                  <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                  <span class="text-primary small fw-bold">AI Normalization</span>
                  <hr class="flex-grow-1 border-secondary opacity-25;">
                </div>
                <div class="data-row after align-items-center" style="display: flex; gap: 10px; padding: 12px; border-radius: 8px; margin-bottom: 8px; font-family: monospace; font-size: 13px; background: rgba(39, 201, 63, 0.1); border: 1px solid rgba(39, 201, 63, 0.2); color: #e2e8f0;">
                  <div class="col-3 text-truncate">John Doe</div>
                  <div class="col-3 text-truncate">New York, USA</div>
                  <div class="col-4 text-truncate">john@example.com</div>
                  <div class="col-2 text-end text-success"><i class="bi bi-check-circle-fill"></i></div>
                </div>

                <div class="row mt-4 pt-3 border-top border-secondary border-opacity-25 text-center">
                  <div class="col-4">
                    <div class="text-secondary small mb-1">Accuracy</div>
                    <div class="fs-4 fw-bold text-success">99.9%</div>
                  </div>
                  <div class="col-4 border-start border-end border-secondary border-opacity-25">
                    <div class="text-secondary small mb-1">Duplicates Fixed</div>
                    <div class="fs-4 fw-bold text-white">1,402</div>
                  </div>
                  <div class="col-4">
                    <div class="text-secondary small mb-1">Time Saved</div>
                    <div class="fs-4 fw-bold text-primary">45h</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Floating Elements -->
            <div class="floating-badge float-anim-1" style="position: absolute; top: 20px; right: -20px; background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); padding: 12px 20px; border-radius: 100px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); display: flex; align-items: center; gap: 10px; font-weight: 600; font-size: 14px; color: #0f172a; z-index: 10;">
              <i class="bi bi-shield-check text-success fs-5"></i> Data Validated
            </div>
            <div class="floating-badge float-anim-2" style="position: absolute; bottom: 40px; left: -30px; background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); padding: 12px 20px; border-radius: 100px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); display: flex; align-items: center; gap: 10px; font-weight: 600; font-size: 14px; color: #0f172a; z-index: 10;">
              <i class="bi bi-robot text-primary fs-5"></i> AI Active
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Logo Cloud -->
    <section class="py-5 border-top border-bottom bg-white">
      <div class="container">
        <p class="text-center text-secondary small fw-bold text-uppercase tracking-wider mb-4">Trusted by innovative teams worldwide</p>
        <div class="d-flex justify-content-center align-items-center flex-wrap gap-4 gap-lg-5">
          <i class="bi bi-stripe" style="font-size: 2.5rem; color: #94a3b8;"></i>
          <i class="bi bi-spotify" style="font-size: 2.5rem; color: #94a3b8;"></i>
          <i class="bi bi-slack" style="font-size: 2.5rem; color: #94a3b8;"></i>
          <i class="bi bi-github" style="font-size: 2.5rem; color: #94a3b8;"></i>
          <i class="bi bi-dropbox" style="font-size: 2.5rem; color: #94a3b8;"></i>
          <i class="bi bi-microsoft" style="font-size: 2.5rem; color: #94a3b8;"></i>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section id="features" class="py-5 bg-white">
      <div class="container py-5">
        <div class="text-center mb-5 mx-auto" style="max-width: 600px;">
          <h2 class="display-5 fw-bold mb-3">Powerful Tools for <br>Data Engineers</h2>
          <p class="text-secondary fs-5">Everything you need to maintain a pristine, production-ready data ecosystem without writing a single script.</p>
        </div>
        
        <div class="row g-4">
          <div class="col-md-6 col-lg-4">
            <div class="feature-card h-100 p-4 p-xl-5" style="background: #ffffff; border-radius: 16px; border: 1px solid rgba(0,0,0,0.05); transition: all 0.3s ease;">
              <div class="icon-box bg-primary bg-opacity-10 text-primary" style="width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 20px;">
                <i class="bi bi-intersect"></i>
              </div>
              <h4 class="mb-3">AI Deduplication</h4>
              <p class="text-secondary mb-0">Fuzzy matching algorithms that find duplicate records across messy datasets with 99% accuracy, even with typos.</p>
            </div>
          </div>
          <div class="col-md-6 col-lg-4">
            <div class="feature-card h-100 p-4 p-xl-5" style="background: #ffffff; border-radius: 16px; border: 1px solid rgba(0,0,0,0.05); transition: all 0.3s ease;">
              <div class="icon-box bg-info bg-opacity-10 text-info" style="width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 20px;">
                <i class="bi bi-geo-alt"></i>
              </div>
              <h4 class="mb-3">Address Standardizing</h4>
              <p class="text-secondary mb-0">Verify and format global addresses against official postal databases in real-time to ensure deliverability.</p>
            </div>
          </div>
          <div class="col-md-6 col-lg-4">
            <div class="feature-card h-100 p-4 p-xl-5" style="background: #ffffff; border-radius: 16px; border: 1px solid rgba(0,0,0,0.05); transition: all 0.3s ease;">
              <div class="icon-box bg-success bg-opacity-10 text-success" style="width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 20px;">
                <i class="bi bi-shield-lock"></i>
              </div>
              <h4 class="mb-3">PII Protection</h4>
              <p class="text-secondary mb-0">Automatically detect and securely mask sensitive information like emails, SSNs, and phone numbers.</p>
            </div>
          </div>
          <div class="col-md-6 col-lg-4">
            <div class="feature-card h-100 p-4 p-xl-5" style="background: #ffffff; border-radius: 16px; border: 1px solid rgba(0,0,0,0.05); transition: all 0.3s ease;">
              <div class="icon-box bg-warning bg-opacity-10 text-warning" style="width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 20px;">
                <i class="bi bi-diagram-3"></i>
              </div>
              <h4 class="mb-3">Schema Mapping</h4>
              <p class="text-secondary mb-0">Intelligent field mapping that learns your data structure and automates future imports from similar sources.</p>
            </div>
          </div>
          <div class="col-md-6 col-lg-4">
            <div class="feature-card h-100 p-4 p-xl-5" style="background: #ffffff; border-radius: 16px; border: 1px solid rgba(0,0,0,0.05); transition: all 0.3s ease;">
              <div class="icon-box bg-danger bg-opacity-10 text-danger" style="width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 20px;">
                <i class="bi bi-database-add"></i>
              </div>
              <h4 class="mb-3">Data Enrichment</h4>
              <p class="text-secondary mb-0">Enhance missing data points with external signals like company size, industry, and social profiles via Clearbit.</p>
            </div>
          </div>
          <div class="col-md-6 col-lg-4">
            <div class="feature-card h-100 p-4 p-xl-5" style="background: #ffffff; border-radius: 16px; border: 1px solid rgba(0,0,0,0.05); transition: all 0.3s ease;">
              <div class="icon-box bg-dark bg-opacity-10 text-dark" style="width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 20px;">
                <i class="bi bi-terminal"></i>
              </div>
              <h4 class="mb-3">API First</h4>
              <p class="text-secondary mb-0">Everything you can do in the UI is available via our robust, high-performance REST and GraphQL API.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Process Section -->
    <section class="py-5">
      <div class="container py-5">
        <div class="row align-items-center">
          <div class="col-lg-5 mb-5 mb-lg-0">
            <h2 class="display-6 fw-bold mb-4">Go from raw mess to production-ready in record time.</h2>
            
            <div class="nav flex-column nav-pills gap-2 mb-4">
              <button v-for="(step, key) in processSteps" :key="key"
                @click="activeTab = key"
                class="nav-link text-start d-flex align-items-center gap-3 rounded-pill"
                :class="activeTab === key ? 'active' : ''"
                style="padding: 10px 24px; font-weight: 600;">
                <div class="bg-light rounded p-2" :class="activeTab === key ? step.colorClass : 'text-secondary'">
                  <i class="bi fs-5" :class="step.icon"></i>
                </div>
                <span class="fs-5">{{ step.title }}</span>
              </button>
            </div>
          </div>
          
          <div class="col-lg-6 offset-lg-1">
            <transition name="fade" mode="out-in">
              <div :key="activeTab" class="process-image-container position-relative overflow-hidden" style="background: #ffffff; border-radius: 24px; padding: 40px; box-shadow: 0 20px 40px -10px rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.05); aspect-ratio: 1/1; display: flex; align-items: center; justify-content: center;">
                <div class="text-center">
                  <div class="rounded-circle bg-light d-inline-flex align-items-center justify-content-center mb-4 shadow-sm" style="width: 120px; height: 120px;">
                    <i class="bi display-3" :class="[processSteps[activeTab].icon, processSteps[activeTab].colorClass]"></i>
                  </div>
                  <h3 class="h2 mb-3">{{ processSteps[activeTab].title }}</h3>
                  <p class="text-secondary fs-5 mb-4">{{ processSteps[activeTab].desc }}</p>
                  
                  <ul class="list-unstyled text-start d-inline-block">
                    <li v-for="bullet in processSteps[activeTab].bullets" :key="bullet" class="mb-2 d-flex align-items-center gap-2 text-secondary fw-medium">
                      <i class="bi bi-check-circle-fill text-success"></i> {{ bullet }}
                    </li>
                  </ul>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonials -->
    <section class="py-5 bg-white border-top">
      <div class="container py-5">
        <div class="text-center mb-5">
          <h2 class="display-6 fw-bold mb-3">Loved by Data Teams</h2>
          <p class="text-secondary fs-5">Don't just take our word for it.</p>
        </div>
        <div class="row g-4">
          <div class="col-md-4">
            <div class="card h-100 border-0 p-4" style="background: #f8fafc; border-radius: 16px;">
              <div class="text-warning mb-3"><i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i></div>
              <p class="fs-5 mb-4">"MasterDataCleaner saved our team over 200 hours of manual Excel work in just the first month. The ROI was immediate."</p>
              <div class="d-flex align-items-center mt-auto">
                <img src="https://i.pravatar.cc/150?u=sarah" alt="Sarah" class="rounded-circle me-3" style="width: 48px; height: 48px;">
                <div>
                  <h6 class="fw-bold mb-0">Sarah Chen</h6>
                  <p class="small text-secondary mb-0">Lead Data Engineer, TechFlow</p>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card h-100 border-0 p-4" style="background: #f8fafc; border-radius: 16px;">
              <div class="text-warning mb-3"><i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i></div>
              <p class="fs-5 mb-4">"The AI deduplication is magic. It found fuzzy matches we would have never seen manually. Absolutely essential tool."</p>
              <div class="d-flex align-items-center mt-auto">
                <img src="https://i.pravatar.cc/150?u=marcus" alt="Marcus" class="rounded-circle me-3" style="width: 48px; height: 48px;">
                <div>
                  <h6 class="fw-bold mb-0">Marcus Thorne</h6>
                  <p class="small text-secondary mb-0">VP of Operations, LogiGlobal</p>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card h-100 border-0 p-4" style="background: #f8fafc; border-radius: 16px;">
              <div class="text-warning mb-3"><i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i><i class="bi bi-star-fill"></i></div>
              <p class="fs-5 mb-4">"Security was our main concern, and their SOC 2 compliance combined with automated PII masking made it an easy choice."</p>
              <div class="d-flex align-items-center mt-auto">
                <img src="https://i.pravatar.cc/150?u=elena" alt="Elena" class="rounded-circle me-3" style="width: 48px; height: 48px;">
                <div>
                  <h6 class="fw-bold mb-0">Elena Rodriguez</h6>
                  <p class="small text-secondary mb-0">CISO, FinSecure</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Pricing -->
    <section id="pricing" class="py-5">
      <div class="container py-5">
        <div class="text-center mb-5">
          <h2 class="display-5 fw-bold mb-3">Simple, transparent pricing</h2>
          <p class="text-secondary fs-5 mb-4">Start free, scale as your data grows.</p>
          
          <!-- Toggle -->
          <div class="d-flex align-items-center justify-content-center gap-3">
            <span :class="{'fw-bold': !isAnnual, 'text-secondary': isAnnual}">Monthly</span>
            <div class="form-check form-switch fs-4 mb-0">
              <input class="form-check-input shadow-none" type="checkbox" role="switch" v-model="isAnnual" style="cursor: pointer;">
            </div>
            <span :class="{'fw-bold': isAnnual, 'text-secondary': !isAnnual}">
              Annually <span class="badge bg-success bg-opacity-10 text-success rounded-pill fs-6 ms-1">Save 20%</span>
            </span>
          </div>
        </div>

        <div class="row align-items-center justify-content-center g-4 max-w-5xl mx-auto">
          <!-- Free Tier -->
          <div class="col-lg-4">
            <div class="p-4 p-xl-5" style="background: white; border-radius: 24px; border: 1px solid rgba(0,0,0,0.08);">
              <h3 class="fw-bold mb-1">Starter</h3>
              <p class="text-secondary mb-4">Perfect for trying out the platform</p>
              <div class="mb-4">
                <span class="display-4 fw-bold">$0</span>
                <span class="text-secondary">/ forever</span>
              </div>
              <BButton variant="outline-dark" class="w-100 rounded-pill fw-bold py-2 mb-4" @click="goToDashboard">
                Get Started Free
              </BButton>
              <ul class="list-unstyled mb-0 d-flex flex-column gap-3">
                <li class="d-flex align-items-center gap-2"><i class="bi bi-check2 text-primary fs-5"></i> 1 Project</li>
                <li class="d-flex align-items-center gap-2"><i class="bi bi-check2 text-primary fs-5"></i> 1,000 rows per dataset</li>
                <li class="d-flex align-items-center gap-2"><i class="bi bi-check2 text-primary fs-5"></i> Basic cleaning rules</li>
                <li class="d-flex align-items-center gap-2"><i class="bi bi-check2 text-primary fs-5"></i> CSV import/export</li>
                <li class="d-flex align-items-center gap-2 text-secondary opacity-50"><i class="bi bi-x fs-5"></i> AI features</li>
              </ul>
            </div>
          </div>

          <!-- Pro Tier -->
          <div class="col-lg-4">
            <div class="p-4 p-xl-5" style="background: white; border-radius: 24px; border: 2px solid var(--primary-color); box-shadow: 0 20px 40px -15px rgba(79, 70, 229, 0.15); position: relative;">
              <div style="position: absolute; top: -14px; left: 50%; transform: translateX(-50%); background: var(--primary-color); color: white; padding: 4px 16px; border-radius: 20px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">Most Popular</div>
              <h3 class="fw-bold mb-1" style="color: var(--primary-color);">Pro</h3>
              <p class="text-secondary mb-4">For professionals and small teams</p>
              <div class="mb-4 d-flex align-items-baseline">
                <span class="display-4 fw-bold">${{ isAnnual ? '24' : '29' }}</span>
                <span class="text-secondary ms-1">/ mo</span>
              </div>
              <p class="small text-success mb-3 mt-n2" v-if="isAnnual">Billed $288 yearly</p>
              <p class="small mb-3 mt-n2" v-else style="height: 18px;"></p>
              <BButton variant="primary" class="w-100 rounded-pill fw-bold py-2 mb-4" @click="goToDashboard">
                Start 14-Day Free Trial
              </BButton>
              <ul class="list-unstyled mb-0 d-flex flex-column gap-3">
                <li class="d-flex align-items-center gap-2"><i class="bi bi-check2 text-primary fs-5"></i> Unlimited Projects</li>
                <li class="d-flex align-items-center gap-2"><i class="bi bi-check2 text-primary fs-5"></i> 100k rows per dataset</li>
                <li class="d-flex align-items-center gap-2 fw-bold"><i class="bi bi-stars text-warning fs-5"></i> Full AI Cleaning Suite</li>
                <li class="d-flex align-items-center gap-2"><i class="bi bi-check2 text-primary fs-5"></i> API Access</li>
                <li class="d-flex align-items-center gap-2"><i class="bi bi-check2 text-primary fs-5"></i> 3 Team Members</li>
              </ul>
            </div>
          </div>

          <!-- Enterprise Tier -->
          <div class="col-lg-4">
            <div class="p-4 p-xl-5" style="background: white; border-radius: 24px; border: 1px solid rgba(0,0,0,0.08);">
              <h3 class="fw-bold mb-1">Enterprise</h3>
              <p class="text-secondary mb-4">For larger scale organizations</p>
              <div class="mb-4">
                <span class="display-5 fw-bold">Custom</span>
              </div>
              <BButton variant="outline-dark" class="w-100 rounded-pill fw-bold py-2 mb-4">
                Contact Sales
              </BButton>
              <ul class="list-unstyled mb-0 d-flex flex-column gap-3">
                <li class="d-flex align-items-center gap-2"><i class="bi bi-check2 text-primary fs-5"></i> Unlimited Everything</li>
                <li class="d-flex align-items-center gap-2"><i class="bi bi-check2 text-primary fs-5"></i> Custom Integrations</li>
                <li class="d-flex align-items-center gap-2"><i class="bi bi-check2 text-primary fs-5"></i> Dedicated Success Manager</li>
                <li class="d-flex align-items-center gap-2"><i class="bi bi-check2 text-primary fs-5"></i> SSO / SAML</li>
                <li class="d-flex align-items-center gap-2"><i class="bi bi-check2 text-primary fs-5"></i> On-premise option</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section class="py-5 bg-white border-top">
      <div class="container py-5" style="max-width: 800px;">
        <h2 class="display-6 fw-bold text-center mb-5">Frequently Asked Questions</h2>
        
        <div class="accordion" id="faqAccordion">
          <div class="accordion-item" style="border: none; border-bottom: 1px solid rgba(0,0,0,0.08); background: transparent;">
            <h2 class="accordion-header">
              <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#faq1" style="background: transparent; font-weight: 600; font-size: 1.1rem; color: var(--dark-color); padding: 20px 0; box-shadow: none;">
                How do you ensure data privacy and security?
              </button>
            </h2>
            <div id="faq1" class="accordion-collapse collapse show" data-bs-parent="#faqAccordion">
              <div class="accordion-body" style="padding: 0 0 20px 0; color: #64748b; line-height: 1.7;">
                We take security seriously. We are SOC 2 Type II compliant. Your data is encrypted at rest (AES-256) and in transit (TLS 1.3). We do not train our foundational AI models on your proprietary data. For enterprise customers, we also offer secure on-premise deployment options.
              </div>
            </div>
          </div>
          <div class="accordion-item" style="border: none; border-bottom: 1px solid rgba(0,0,0,0.08); background: transparent;">
            <h2 class="accordion-header">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq2" style="background: transparent; font-weight: 600; font-size: 1.1rem; color: var(--dark-color); padding: 20px 0; box-shadow: none;">
                Which file formats and databases do you support?
              </button>
            </h2>
            <div id="faq2" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
              <div class="accordion-body" style="padding: 0 0 20px 0; color: #64748b; line-height: 1.7;">
                Out of the box, we support flat files like CSV, Excel (XLSX), JSON, XML, Parquet, and Avro. We also feature native, real-time connectors for Snowflake, BigQuery, AWS Redshift, PostgreSQL, MongoDB, and popular CRMs like Salesforce and HubSpot.
              </div>
            </div>
          </div>
          <div class="accordion-item" style="border: none; border-bottom: 1px solid rgba(0,0,0,0.08); background: transparent;">
            <h2 class="accordion-header">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq3" style="background: transparent; font-weight: 600; font-size: 1.1rem; color: var(--dark-color); padding: 20px 0; box-shadow: none;">
                How accurate is the AI cleaning and deduplication?
              </button>
            </h2>
            <div id="faq3" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
              <div class="accordion-body" style="padding: 0 0 20px 0; color: #64748b; line-height: 1.7;">
                Our proprietary fuzzy matching models are trained on billions of real-world data points. In benchmark tests, they consistently achieve over 99.5% accuracy in deduplication and normalization tasks, significantly outperforming traditional Levenshtein distance rules. You can also adjust the confidence thresholds manually.
              </div>
            </div>
          </div>
          <div class="accordion-item" style="border: none; border-bottom: 1px solid rgba(0,0,0,0.08); background: transparent;">
            <h2 class="accordion-header">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq4" style="background: transparent; font-weight: 600; font-size: 1.1rem; color: var(--dark-color); padding: 20px 0; box-shadow: none;">
                Can I build custom cleaning rules specific to my business?
              </button>
            </h2>
            <div id="faq4" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
              <div class="accordion-body" style="padding: 0 0 20px 0; color: #64748b; line-height: 1.7;">
                Absolutely! While our AI handles the heavy lifting, you can use our visual rule builder (If/Then logic) or write custom Python/JavaScript snippets within the platform to handle complex, domain-specific business logic.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="py-5 text-white position-relative overflow-hidden" style="background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));">
      <div class="position-absolute w-100 h-100 start-0 top-0" style="background: url('data:image/svg+xml,%3Csvg width=%2760%27 height=%2760%27 viewBox=%270 0 60 60%27 xmlns=%27http://www.w3.org/2000/svg%27%3E%3Cg fill=%27none%27 fill-rule=%27evenodd%27%3E%3Cg fill=%27%23ffffff%27 fill-opacity=%270.05%27%3E%3Cpath d=%27M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z%27/%3E%3C/g%3E%3C/g%3E%3C/svg%27');"></div>
      <div class="container py-5 text-center position-relative z-1">
        <h2 class="display-4 fw-bold mb-3">Ready to transform your data?</h2>
        <p class="fs-4 mb-5 opacity-75 fw-light">Join thousands of teams already using MasterDataCleaner to automate their workflows.</p>
        <div class="d-flex flex-column flex-sm-row justify-content-center gap-3">
          <BButton variant="light" size="lg" class="rounded-pill px-5 fw-bold" style="color: var(--primary-color);" @click="goToDashboard">
            Start Free Trial
          </BButton>
          <BButton variant="outline-light" size="lg" class="rounded-pill px-5 fw-bold">
            Contact Sales
          </BButton>
        </div>
        <p class="mt-4 small opacity-75">No credit card required. 14-day free trial.</p>
      </div>
    </section>

    <!-- Footer -->
    <footer class="py-5" style="background-color: #0f172a; color: #cbd5e1;">
      <div class="container py-4">
        <div class="row g-4 mb-5">
          <div class="col-lg-4 pe-lg-5">
            <a href="#" class="fs-4 fw-bold text-white text-decoration-none d-flex align-items-center gap-2 mb-3" @click.prevent="$router.push('/')">
              <i class="bi bi-stars text-primary"></i> MasterDataCleaner
            </a>
            <p class="small text-secondary mb-4 pe-lg-4">The ultimate platform for cleaning, normalizing, and enriching your master data with AI precision. Built for modern data teams.</p>
            <div class="d-flex gap-3">
              <a href="#" class="bg-secondary bg-opacity-10 p-2 rounded text-secondary" style="text-decoration: none;"><i class="bi bi-twitter-x"></i></a>
              <a href="#" class="bg-secondary bg-opacity-10 p-2 rounded text-secondary" style="text-decoration: none;"><i class="bi bi-github"></i></a>
              <a href="#" class="bg-secondary bg-opacity-10 p-2 rounded text-secondary" style="text-decoration: none;"><i class="bi bi-linkedin"></i></a>
            </div>
          </div>
          <div class="col-6 col-md-3 col-lg-2">
            <h6 class="fw-bold text-white mb-4">Product</h6>
            <ul class="list-unstyled mb-0 d-flex flex-column gap-2 small">
              <li><a href="#features">Features</a></li>
              <li><a href="#integrations">Integrations</a></li>
              <li><a href="#pricing">Pricing</a></li>
              <!-- <li><a href="#">Changelog</a></li> -->
              <!-- <li><a href="#">API Docs</a></li> -->
            </ul>
          </div>
          <div class="col-6 col-md-3 col-lg-2">
            <h6 class="fw-bold text-white mb-4">Company</h6>
            <ul class="list-unstyled mb-0 d-flex flex-column gap-2 small">
              <!-- <li><a href="#">About Us</a></li> -->
              <!-- <li><a href="#">Careers</a></li> -->
              <!-- <li><a href="#">Blog</a></li> -->
              <li><a href="#">Contact</a></li>
              <!-- <li><a href="#">Partners</a></li> -->
            </ul>
          </div>
          <div class="col-6 col-md-3 col-lg-2">
            <h6 class="fw-bold text-white mb-4">Support</h6>
            <ul class="list-unstyled mb-0 d-flex flex-column gap-2 small">
              <!-- <li><a href="#">Help Center</a></li>
              <li><a href="#">Community</a></li>
              <li><a href="#">Status</a></li> -->
              <li><a href="#">Security</a></li>
            </ul>
          </div>
          <div class="col-6 col-md-3 col-lg-2">
            <h6 class="fw-bold text-white mb-4">Legal</h6>
            <ul class="list-unstyled mb-0 d-flex flex-column gap-2 small">
              <li><a href="#">Privacy Policy</a></li>
              <!-- <li><a href="#">Terms of Service</a></li>
              <li><a href="#">Cookie Policy</a></li>
              <li><a href="#">DPA</a></li> -->
            </ul>
          </div>
        </div>
        
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-center pt-4" style="border-top: 1px solid rgba(255,255,255,0.1);">
          <p class="small text-secondary mb-2 mb-md-0">© 2024 MasterDataCleaner Inc. All rights reserved.</p>
          <p class="small text-secondary mb-0">Made with <i class="bi bi-heart-fill text-danger mx-1"></i> for data teams</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const toast = useToast()
const activeTab = ref('connect')
const isAnnual = ref(true)

const processSteps = {
  connect: { 
    title: 'Import from Anywhere', 
    desc: 'Connect directly to your cloud databases, CRMs, or drag and drop flat files securely.', 
    icon: 'bi-database-up', 
    colorClass: 'text-primary',
    bullets: ['50+ native integrations', 'CSV, Excel, JSON support', 'Secure API endpoints']
  },
  analyze: { 
    title: 'Auto-Profile & Analyze', 
    desc: 'Our AI instantly profiles your data, identifying anomalies, missing values, and schema structures.', 
    icon: 'bi-search', 
    colorClass: 'text-warning',
    bullets: ['Instant data quality score', 'Anomaly detection', 'Automatic schema mapping']
  },
  clean: { 
    title: 'Clean & Normalize', 
    desc: 'Apply pre-built AI models to deduplicate, standardise addresses, and fix formatting issues.', 
    icon: 'bi-magic', 
    colorClass: 'text-success',
    bullets: ['Fuzzy deduplication', 'Address standardization', 'Custom rule builder']
  },
  export: { 
    title: 'Sync & Export', 
    desc: 'Push your pristine data back to your systems or download it in your preferred format.', 
    icon: 'bi-cloud-download', 
    colorClass: 'text-info',
    bullets: ['Two-way syncing', 'Scheduled exports', 'Webhooks support']
  }
}

function goToDashboard() {
  router.push('/dashboard')
}

function watchDemo() {
  // Could open a modal or YouTube link
  toast.info('Demo video coming soon!')
}
</script>

<style scoped>
.hero-section {
  padding-top: 120px;
  padding-bottom: 80px;
  background: radial-gradient(circle at top right, rgba(79, 70, 229, 0.08), transparent 40%), radial-gradient(circle at bottom left, rgba(236, 72, 153, 0.05), transparent 40%);
}

.text-gradient {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.bg-gradient-primary {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px -15px rgba(0,0,0,0.05);
  border-color: rgba(79, 70, 229, 0.2);
}

.float-anim-1 {
  animation: float 6s ease-in-out infinite;
}

.float-anim-2 {
  animation: float 6s ease-in-out infinite;
  animation-delay: 3s;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-15px); }
  100% { transform: translateY(0px); }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Override nav-link styles for process tabs */
:deep(.nav-link) {
  color: #64748b !important;
}

:deep(.nav-link.active) {
  background: white !important;
  color: var(--primary-color) !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  border-color: rgba(0,0,0,0.05);
}
</style>
