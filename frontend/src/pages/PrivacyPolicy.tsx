export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen px-4 py-12">
      <div className="w-full max-w-2xl mx-auto">
        <div className="mb-8 text-center">
          <div className="text-4xl mb-3">🏟️</div>
          <h1 className="text-2xl font-bold">Privacy Policy</h1>
          <p className="text-gray-400 mt-2 text-sm">Goodrec Snooper · Last updated: April 24, 2025</p>
        </div>

        <div className="space-y-6 text-gray-300 text-sm leading-relaxed">
          <section>
            <h2 className="text-white font-semibold text-base mb-2">1. What We Collect</h2>
            <p>
              When you sign up for Goodrec Snooper, we collect your phone number. That's it. We use it
              solely to send you SMS alerts when free host slots open up on Goodrec.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">2. How We Use Your Information</h2>
            <p>Your phone number is used to:</p>
            <ul className="list-disc ml-5 mt-2 space-y-1">
              <li>Verify your identity via one-time passcode (OTP)</li>
              <li>Send you SMS notifications about available Goodrec host slots</li>
              <li>Allow you to manage your alert preferences</li>
            </ul>
            <p className="mt-2">
              We do not sell, share, or rent your phone number to third parties for marketing purposes.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">3. SMS Messaging</h2>
            <p>
              By providing your phone number and signing up, you consent to receiving automated SMS
              messages from Goodrec Snooper. Message frequency varies based on slot availability.
              Message and data rates may apply.
            </p>
            <p className="mt-2">
              To opt out at any time, reply <span className="text-white font-medium">STOP</span> to any
              message we send you. For help, reply <span className="text-white font-medium">HELP</span>.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">4. Third-Party Services</h2>
            <p>
              We use <a href="https://www.twilio.com" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:text-green-300 underline">Twilio</a> to
              deliver SMS messages. Your phone number is transmitted to Twilio for this purpose.
              Twilio's privacy policy is available at{' '}
              <a href="https://www.twilio.com/en-us/legal/privacy" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:text-green-300 underline">
                twilio.com/en-us/legal/privacy
              </a>.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">5. Data Retention</h2>
            <p>
              We retain your phone number and preferences as long as you have an active subscription.
              If you opt out or request deletion, your data is removed from our systems within 30 days.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">6. Your Rights</h2>
            <p>You can request access to, correction of, or deletion of your data at any time by contacting us at the email below.</p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">7. Contact</h2>
            <p>
              Questions? Reach us at{' '}
              <a href="mailto:tobechikeluba@gmail.com" className="text-green-400 hover:text-green-300 underline">
                tobechikeluba@gmail.com
              </a>.
            </p>
          </section>
        </div>

        <div className="mt-10 text-center">
          <a href="/" className="text-green-500 hover:text-green-400 text-sm">← Back to app</a>
        </div>
      </div>
    </div>
  )
}
