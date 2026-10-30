import React, { useState } from 'react';
import { CharacterData } from '../types';

interface AttackModalProps {
  attacker: CharacterData | null;
  characters: CharacterData[];
  isOpen: boolean;
  onClose: () => void;
  onExecuteAttack: (attackerId: number, targetId: number, bodypart: string) => Promise<void>;
}

const BODYPARTS: { key: string; label: string }[] = [
  { key: 'head', label: 'Head' },
  { key: 'torso', label: 'Torso' },
  { key: 'right_arm', label: 'Right Arm' },
  { key: 'left_arm', label: 'Left Arm' },
  { key: 'right_leg', label: 'Right Leg' },
  { key: 'left_leg', label: 'Left Leg' },
];

export const AttackModal: React.FC<AttackModalProps> = ({
  attacker,
  characters,
  isOpen,
  onClose,
  onExecuteAttack,
}) => {
  const [selectedTargetId, setSelectedTargetId] = useState<number | null>(null);
  const [selectedBodypart, setSelectedBodypart] = useState<string>('torso');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  if (!isOpen || !attacker) return null;

  const isAttackerDown =
    attacker.health <= 0 ||
    (Array.isArray(attacker.injury?.general)
      ? attacker.injury.general.includes('down')
      : attacker.injury?.general === 'down');

  // Potential targets: all characters except attacker
  const potentialTargets = characters.filter((c) => c.id !== attacker.id && !c.isNewDraft);
  const selectedTarget = characters.find((c) => c.id === selectedTargetId) || null;

  // Find equipped weapon
  const equippedWeapon = attacker.inventory.find((it) => it.is_weapon) || null;

  const handleConfirmAttack = async () => {
    if (isAttackerDown || !selectedTargetId || !selectedBodypart) return;
    setIsSubmitting(true);
    try {
      await onExecuteAttack(attacker.id, selectedTargetId, selectedBodypart);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="attack-modal-overlay" onClick={onClose}>
      <div className="attack-modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="attack-modal-header">
          <div>
            <div className="attack-modal-title">Select Attack Target</div>
            <div className="attack-modal-subtitle">
              Attacker: <strong style={{ color: '#fff' }}>{attacker.name}</strong>
              {equippedWeapon ? (
                <span>
                  {' '}
                  • Weapon: {equippedWeapon.name} (Ammo: {equippedWeapon.magazine_bullets ?? '-'}/
                  {equippedWeapon.magazine_size ?? '-'})
                </span>
              ) : (
                <span style={{ color: '#f87171' }}> • No weapon equipped!</span>
              )}
            </div>
          </div>
          <button className="attack-modal-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Step 1: Select Target Character */}
        <div className="attack-modal-section">
          <div className="attack-modal-section-title">
            1. Select Target Character {selectedTarget ? `(${selectedTarget.name})` : ''}
          </div>

          {potentialTargets.length === 0 ? (
            <div style={{ padding: '16px', color: '#9aa4b2', textAlign: 'center', fontSize: '0.85rem' }}>
              No other characters in game to attack. Please add an opponent first.
            </div>
          ) : (
            <div className="attack-target-grid">
              {potentialTargets.map((target) => {
                const isSelected = target.id === selectedTargetId;
                const isDown =
                  target.health <= 0 ||
                  (Array.isArray(target.injury?.general)
                    ? target.injury.general.includes('down')
                    : target.injury?.general === 'down');
                return (
                  <div
                    key={target.id}
                    className={`attack-target-card ${isSelected ? 'selected' : ''} ${target.side === 'enemy' ? 'is-enemy' : ''
                      } ${isDown ? 'is-down' : ''}`}
                    onClick={() => setSelectedTargetId(target.id)}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <img
                        src={target.side === 'enemy' ? '/images/enemy.png' : '/images/character.png'}
                        alt={target.side}
                        style={{ width: '24px', height: '24px', objectFit: 'contain' }}
                      />
                      <div style={{ overflow: 'hidden' }}>
                        <div className="attack-target-name">{target.name || 'Unnamed Unit'}</div>
                        <div style={{ fontSize: '0.7rem', color: target.side === 'enemy' ? '#f87171' : '#38bdf8' }}>
                          {target.side.toUpperCase()}
                        </div>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span className={`health-badge ${target.health <= 2 ? 'critical' : ''}`}>
                        HP: {target.health}
                      </span>
                      {isDown && <img src="/images/down.png" alt="Down" style={{ width: '16px', height: '16px' }} />}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Step 2: Select Target Bodypart */}
        <div className="attack-modal-section">
          <div className="attack-modal-section-title">
            2. Select Target Bodypart {selectedBodypart ? `(${selectedBodypart.toUpperCase()})` : ''}
          </div>

          <div className="attack-bodypart-grid">
            {BODYPARTS.map((bp) => {
              const isSelected = selectedBodypart === bp.key;
              const bpHealth = selectedTarget
                ? (selectedTarget as any)[bp.key] ?? '-'
                : null;
              const isInjured = selectedTarget
                ? !!selectedTarget.injury?.[bp.key as keyof typeof selectedTarget.injury] &&
                selectedTarget.injury[bp.key as keyof typeof selectedTarget.injury] !== 'None'
                : false;

              return (
                <button
                  key={bp.key}
                  type="button"
                  className={`attack-bodypart-btn ${isSelected ? 'selected' : ''}`}
                  onClick={() => setSelectedBodypart(bp.key)}
                >
                  <span className="bodypart-label">{bp.label}</span>
                  {selectedTarget && (
                    <span className="bodypart-hp">
                      HP: {bpHealth}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Actions */}
        {isAttackerDown && (
          <div style={{ color: '#ef4444', textAlign: 'center', marginBottom: '8px', fontSize: '0.85rem', fontWeight: 600 }}>
            Attacker is down and cannot perform an attack!
          </div>
        )}
        <div className="attack-modal-actions">
          <button className="btn-action" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </button>

          <button
            className="btn-action attack-strike-btn"
            disabled={!selectedTargetId || !selectedBodypart || isSubmitting || isAttackerDown}
            onClick={handleConfirmAttack}
          >
            {isSubmitting ? 'Attacking...' : isAttackerDown ? 'Attacker Down' : `Attack`}
          </button>
        </div>
      </div>
    </div>
  );
};
