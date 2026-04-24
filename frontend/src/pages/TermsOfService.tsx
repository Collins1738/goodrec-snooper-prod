export default function TermsOfService() {
  return (
    <div className="min-h-screen px-4 py-12">
      <div className="w-full max-w-2xl mx-auto">
        <div className="mb-8 text-center">
          <div className="text-4xl mb-3">🏟️</div>
          <h1 className="text-2xl font-bold">Terms of Service</h1>
          <p className="text-gray-400 mt-2 text-sm">Goodrec Snooper · Last updated: April 24, 2025</p>
        </div>

        <div className="space-y-6 text-gray-300 text-sm leading-relaxed">
          <section>
            <h2 className="text-white font-semibold text-base mb-2">1. About the Service</h2>
            <p>
              Goodrec Snooper is an unofficial notification service that monitors Goodrec for available
              free host slots and sends you SMS alerts. We are not affiliated with Goodrec.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">2. Eligibility</h2>
            <p>
              By using this service, you confirm that you are at least 13 years old, that you own or
              have permission to use the phone number you provide, and that you consent to receiving
              automated SMS messages.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">3. SMS Consent</h2>
            <p>
              By signing up, you agree to receive recurring automated text messages from Goodrec Snooper
              at the phone number you provide. Message frequency depends on slot availability. Message
              and data rates may apply.
            </p>
            <p className="mt-2">
              To stop receiving messages, reply <span className="text-white font-medium">STOP</span> to
              any message. For help, reply <span className="text-white font-medium">HELP</span>. You may
              also update your preferences or unsubscribe from within the app.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">4. No Guarantees</h2>
            <p>
              We do our best to send timely notifications, but we make no guarantees about slot
              availability, notification delivery, or uptime. Goodrec Snooper is provided "as is"
              without warranty of any kind.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">5. Acceptable Use</h2>
            <p>You agree not to:</p>
            <ul className="list-disc ml-5 mt-2 space-y-1">
              <li>Provide a phone number that is not yours</li>
              <li>Use the service for any unlawful purpose</li>
              <li>Attempt to reverse engineer, abuse, or disrupt the service</li>
            </ul>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">6. Limitation of Liability</h2>
            <p>
              To the fullest extent permitted by law, Goodrec Snooper is not liable for any indirect,
              incidental, or consequential damages arising from your use of the service.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">7. Changes to These Terms</h2>
            <p>
              We may update these terms from time to time. Continued use of the service after changes
              are posted means you accept the updated terms.
            </p>
          </section>

          <section>
            <h2 className="text-white font-semibold text-base mb-2">8. Contact</h2>
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
