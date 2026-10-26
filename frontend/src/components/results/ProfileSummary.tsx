import type { ProfileSummary as Profile } from '../../types/assessment'
import { GlassCard } from '../common/GlassCard'

export function ProfileSummary({ profile }: { profile: Profile }) {
  return (
    <GlassCard as="section" className="profile-summary" labelledBy="profile-heading" subtle>
      <h2 id="profile-heading">Your answers</h2>
      <dl className="profile-grid">
        <div>
          <dt>Age</dt>
          <dd>
            {profile.age_years} <span className="muted">(age group {profile.age_group})</span>
          </dd>
        </div>
        <div>
          <dt>Height</dt>
          <dd>{profile.height_cm !== null ? `${profile.height_cm} cm` : 'Not given'}</dd>
        </div>
        <div>
          <dt>Weight</dt>
          <dd>{profile.weight_kg !== null ? `${profile.weight_kg} kg` : 'Not given'}</dd>
        </div>
        <div>
          <dt>
            BMI <span className="chip">derived</span>
          </dt>
          <dd>
            {profile.bmi ? (
              <>
                {profile.bmi.value} <span className="muted">({profile.bmi.who_category}, {profile.bmi.source})</span>
              </>
            ) : (
              'Not calculated (height or weight not given)'
            )}
          </dd>
        </div>
        {profile.answers.map((answer) => (
          <div key={answer.field}>
            <dt>{answer.question}</dt>
            <dd>{answer.label}</dd>
          </div>
        ))}
      </dl>
    </GlassCard>
  )
}
