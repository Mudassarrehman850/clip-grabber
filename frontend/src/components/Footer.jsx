import React, { useState } from 'react';
import Modal from './Modal';

export default function Footer() {
  const currentYear = new Date().getFullYear();
  const [activeModal, setActiveModal] = useState(null);

  const closeModal = () => setActiveModal(null);

  return (
    <footer className="relative z-10 py-16 mt-16 border-t border-border-color">
      <div className="max-w-4xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
            
            <div className="space-y-4 text-center md:text-left">
                <div className="text-2xl font-black tracking-tight text-text-primary">
                    Clip<span className="text-brand">Grabber</span>
                </div>
                <p className="text-xs font-bold text-text-muted leading-relaxed max-w-sm mx-auto md:mx-0">
                    Your professional-grade media toolkit. Fast, private, and always secure.
                </p>
                <div className="text-[0.6rem] font-black text-brand uppercase tracking-[0.2em]">
                    Premium Quality • No Tracking • High Speed
                </div>
            </div>

            <div className="space-y-6 text-center md:text-right">
                <div className="flex flex-wrap items-center justify-center md:justify-end gap-x-6 gap-y-2 text-[0.7rem] font-bold text-text-secondary uppercase tracking-widest">
                    <button onClick={() => setActiveModal('tos')} className="hover:text-brand transition-colors">Terms of Service</button>
                    <button onClick={() => setActiveModal('privacy')} className="hover:text-brand transition-colors">Privacy Policy</button>
                    <button onClick={() => setActiveModal('contact')} className="hover:text-brand transition-colors">Support</button>
                </div>
                
                <div className="space-y-1">
                    <p className="text-[0.65rem] font-bold text-text-muted opacity-60">
                        © {currentYear} ClipGrabber. All Rights Reserved. Not affiliated with TikTok, Instagram, or YouTube.
                    </p>
                    <p className="text-[0.6rem] font-bold text-text-muted opacity-40 uppercase tracking-widest">
                        Built for the community • Powered by Mudassar Rehman
                    </p>
                </div>
            </div>

        </div>

        {/* Legal modals */}
        <Modal 
          isOpen={activeModal === 'tos'} 
          onClose={closeModal} 
          title="Terms of Service"
        >
          <div className="space-y-6">
            <h4 className="text-text-primary font-black uppercase tracking-wider">1. Acceptance of Terms</h4>
            <p>By accessing and using ClipGrabber, you accept and agree to be bound by the terms and provision of this agreement. Our service allows you to download publicly available media for personal, non-commercial use only.</p>
            
            <h4 className="text-text-primary font-black uppercase tracking-wider">2. Use License</h4>
            <p>You may not use this service to infringe upon the intellectual property rights of others. You are solely responsible for ensuring you have the right to download any content you process through ClipGrabber.</p>
            
            <h4 className="text-text-primary font-black uppercase tracking-wider">3. Limitations</h4>
            <p>In no event shall ClipGrabber or its suppliers be liable for any damages arising out of the use or inability to use the materials on ClipGrabber website.</p>
          </div>
        </Modal>

        <Modal 
          isOpen={activeModal === 'privacy'} 
          onClose={closeModal} 
          title="Privacy Policy"
        >
          <div className="space-y-6">
            <h4 className="text-text-primary font-black uppercase tracking-wider">Data Collection</h4>
            <p>We do not collect personal information. We do not store your IP address, your download history, or any identifying metadata. Our system operates in a stateless "RAM-only" environment, purging all processed file data immediately after your download is complete.</p>
            
            <h4 className="text-text-primary font-black uppercase tracking-wider">Cookies</h4>
            <p>We use a single "theme" cookie to remember your preference for Light or Dark mode. We do not use tracking cookies or third-party behavioral analytics.</p>
          </div>
        </Modal>

        <Modal 
          isOpen={activeModal === 'contact'} 
          onClose={closeModal} 
          title="Contact Expert Support"
        >
          <div className="space-y-8 py-4">
            <div className="text-center space-y-2">
                <p className="text-xl font-black text-text-primary tracking-tight">Need help or a custom feature?</p>
                <p className="text-sm font-medium text-text-secondary">Reach out directly to the lead developer for priority assistance.</p>
            </div>
            
            <div className="grid grid-cols-1 gap-4">
                <a href="mailto:mudassar1rehman@gmail.com" className="group block p-8 rounded-3xl bg-brand/[0.03] border-2 border-brand/10 hover:border-brand/40 transition-all text-center">
                    <div className="w-12 h-12 rounded-2xl bg-brand/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>
                        </svg>
                    </div>
                    <p className="text-[0.65rem] font-black uppercase tracking-[0.2em] text-brand mb-1">Direct Email</p>
                    <p className="text-lg font-bold text-text-primary">mudassar1rehman@gmail.com</p>
                </a>
                
                <a href="https://www.linkedin.com/in/mudassar-rehman-2558253b2" target="_blank" rel="noreferrer" className="group block p-8 rounded-3xl bg-[#0077B5]/[0.03] border-2 border-[#0077B5]/10 hover:border-[#0077B5]/40 transition-all text-center">
                    <div className="w-12 h-12 rounded-2xl bg-[#0077B5]/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                        <svg width="24" height="24" fill="#0077B5" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
                    </div>
                    <p className="text-[0.65rem] font-black uppercase tracking-[0.2em] text-[#0077B5] mb-1">Professional Network</p>
                    <p className="text-lg font-bold text-text-primary">Connect on LinkedIn</p>
                </a>
            </div>

            <div className="flex items-center justify-center gap-6 pt-4">
                 <div className="flex flex-col items-center">
                    <span className="text-lg font-bold text-text-primary">24h</span>
                    <span className="text-[0.6rem] font-bold text-text-muted uppercase tracking-widest">Avg Response</span>
                 </div>
                 <div className="w-px h-8 bg-border-color"></div>
                 <div className="flex flex-col items-center">
                    <span className="text-lg font-bold text-text-primary">Global</span>
                    <span className="text-[0.6rem] font-bold text-text-muted uppercase tracking-widest">Coverage</span>
                 </div>
            </div>
          </div>
        </Modal>

        <div className="mt-12 pt-8 border-t border-border-color/30 text-center">
             <p className="text-[0.6rem] font-black text-text-muted/30 uppercase tracking-[0.4em]">
                Powering the future of social archiving
             </p>
        </div>
      </div>
    </footer>
  );
}
