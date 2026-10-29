import React, { useState, useRef, useEffect } from 'react';
import { CharacterData } from '../types';
import { EditableValue } from './EditableValue';

interface CharacterCardProps {
  character: CharacterData;
  isSelected: boolean;
  isCurrentTurn: boolean;
  onSelect: () => void;
  onUpdate: (id: number, updates: Partial<CharacterData>) => void;
  onRandomizeTraits: (id: number, difficulty: number) => void;
  onSaveNewCharacter?: (draft: CharacterData) => void;
  onDeleteCharacter?: (id: number) => void;
  onOpenAttackModal?: (character: CharacterData) => void;
  onToast: (msg: string) => void;
}

export const CharacterCard: React.FC<CharacterCardProps> = ({
  character,
  isSelected,
  isCurrentTurn,
  onSelect,
  onUpdate,
  onRandomizeTraits,
  onSaveNewCharacter,
  onDeleteCharacter,
  onOpenAttackModal,
  onToast,
}) => {
  const [difficulty, setDifficulty] = useState<number>(3);
  const [isEditingName, setIsEditingName] = useState<boolean>(character.isNewDraft || false);
  const [nameDraft, setNameDraft] = useState<string>(character.name);
  const nameInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setNameDraft(character.name);
  }, [character.name]);

  useEffect(() => {
    if (isEditingName && nameInputRef.current) {
      nameInputRef.current.focus();
      nameInputRef.current.select();
    }
  }, [isEditingName]);

  const handleNameCommit = () => {
    setIsEditingName(false);
    const trimmed = nameDraft.trim();
    if (character.isNewDraft) {
      if (trimmed.length > 0 && onSaveNewCharacter) {
        onSaveNewCharacter({ ...character, name: trimmed });
      } else {
        setNameDraft('');
      }
    } else {
      if (trimmed.length > 0 && trimmed !== character.name) {
        onUpdate(character.id, { name: trimmed });
      } else {
        setNameDraft(character.name);
      }
    }
  };

  const handleNameKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleNameCommit();
    } else if (e.key === 'Escape') {
      if (!character.isNewDraft) {
        setIsEditingName(false);
        setNameDraft(character.name);
      }
    }
  };

  // Check injuries
  const isDown = character.health <= 0 || character.injury?.head === 'down';
  const hasHeadInjury = !!character.injury?.head && character.injury.head !== 'None';
  const hasTorsoInjury = !!character.injury?.torso && character.injury.torso !== 'None';
  const hasLeftArmInjury = !!character.injury?.left_arm && character.injury.left_arm !== 'None';
  const hasRightArmInjury = !!character.injury?.right_arm && character.injury.right_arm !== 'None';
  const hasLeftLegInjury = !!character.injury?.left_leg && character.injury.left_leg !== 'None';
  const hasRightLegInjury = !!character.injury?.right_leg && character.injury.right_leg !== 'None';

  const avatarSrc = character.side === 'enemy' ? '/images/enemy.png' : '/images/character.png';

  const handleAttackClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!isCurrentTurn) {
      onToast("Attack is only available to the character whose turn it currently is.");
      return;
    }
    if (character.isNewDraft) {
      onToast('Please enter a name first to save the character before attacking.');
      return;
    }
    if (onOpenAttackModal) {
      onOpenAttackModal(character);
    }
  };

  const handleRandomizeClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (character.isNewDraft) {
      onToast('Please enter a name first to save the character before randomizing.');
      return;
    }
    onRandomizeTraits(character.id, difficulty);
  };

  return (
    <div
      className={`character-card ${character.side === 'enemy' ? 'is-enemy' : ''} ${isSelected ? 'selected' : ''
        } ${isCurrentTurn ? 'active-turn' : ''}`}
      onClick={onSelect}
    >
      {/* Top compact row */}
      <div className="card-top">
        <div className="character-avatar-wrapper">
          <img src={avatarSrc} alt={character.side} className="character-avatar" />
          {isCurrentTurn && <div className="turn-star-badge">Turn</div>}
        </div>

        <div className="card-info">
          <div className="card-name-row">
            {isEditingName ? (
              <input
                ref={nameInputRef}
                type="text"
                placeholder={character.isNewDraft ? 'Enter character name...' : 'Name...'}
                value={nameDraft}
                onChange={(e) => setNameDraft(e.target.value)}
                onBlur={handleNameCommit}
                onKeyDown={handleNameKeyDown}
                onClick={(e) => e.stopPropagation()}
                style={{
                  background: '#0d1117',
                  border: '1px solid #38bdf8',
                  color: '#fff',
                  padding: '2px 6px',
                  borderRadius: '4px',
                  fontWeight: 700,
                  fontSize: '0.95rem',
                  width: '160px',
                }}
              />
            ) : (
              <span
                className="character-name"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsEditingName(true);
                }}
                title="Click to rename"
              >
                {character.name || <span style={{ color: '#ef4444', fontStyle: 'italic' }}>[Set Name]</span>}
              </span>
            )}

            <div className={`health-badge ${character.health <= 2 ? 'critical' : ''}`}>
              <span>HP:</span>
              <span>{character.health}</span>
            </div>
          </div>

          {/* Held weapon badge */}
          {character.held_weapon_name && (
            <div style={{ fontSize: '0.72rem', color: '#e5a93c', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span>Held:</span>
              <strong style={{ color: '#fff' }}>{character.held_weapon_name}</strong>
            </div>
          )}

          {/* Injuries indicator icons */}
          <div className="injuries-container" style={{ marginTop: '4px' }}>
            {isDown && (
              <div className="injury-icon-wrapper" title="down">
                <img src="/images/down.png" alt="down" className="injury-icon" />
                <span className="injury-hover-badge">down</span>
              </div>
            )}
            {hasHeadInjury && !isDown && (
              <div className="injury-icon-wrapper" title={character.injury.head!}>
                <img src="/images/head_injury.png" alt="Head Injury" className="injury-icon" />
                <span className="injury-hover-badge">{character.injury.head}</span>
              </div>
            )}
            {hasTorsoInjury && (
              <div className="injury-icon-wrapper" title={character.injury.torso!}>
                <img src="/images/torso_injury.png" alt="Torso Injury" className="injury-icon" />
                <span className="injury-hover-badge">{character.injury.torso}</span>
              </div>
            )}
            {hasLeftArmInjury && (
              <div className="injury-icon-wrapper" title={character.injury.left_arm!}>
                <img src="/images/left_arm_injury.png" alt="Left Arm Injury" className="injury-icon" />
                <span className="injury-hover-badge">{character.injury.left_arm}</span>
              </div>
            )}
            {hasRightArmInjury && (
              <div className="injury-icon-wrapper" title={character.injury.right_arm!}>
                <img src="/images/right_arm_injury.png" alt="Right Arm Injury" className="injury-icon" />
                <span className="injury-hover-badge">{character.injury.right_arm}</span>
              </div>
            )}
            {hasLeftLegInjury && (
              <div className="injury-icon-wrapper" title={character.injury.left_leg!}>
                <img src="/images/left_leg_injury.png" alt="Left Leg Injury" className="injury-icon" />
                <span className="injury-hover-badge">{character.injury.left_leg}</span>
              </div>
            )}
            {hasRightLegInjury && (
              <div className="injury-icon-wrapper" title={character.injury.right_leg!}>
                <img src="/images/right_leg_injury.png" alt="Right Leg Injury" className="injury-icon" />
                <span className="injury-hover-badge">{character.injury.right_leg}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Expanded view */}
      {isSelected && (
        <div className="expanded-content" onClick={(e) => e.stopPropagation()}>
          {/* Section: Personal Traits */}
          <div>
            <div className="section-label">Personal stats</div>
            <div className="stat-grid-3">
              <EditableValue
                label="Strength"
                value={character.strength}
                onSave={(val) => onUpdate(character.id, { strength: val })}
              />
              <EditableValue
                label="Dexterity"
                value={character.dexterity}
                onSave={(val) => onUpdate(character.id, { dexterity: val })}
              />
              <EditableValue
                label="Toughness"
                value={character.toughness}
                onSave={(val) => onUpdate(character.id, { toughness: val })}
              />
              <EditableValue
                label="Persevere"
                value={character.perseverance}
                onSave={(val) => onUpdate(character.id, { perseverance: val })}
              />
              <EditableValue
                label="Brilliance"
                value={character.brilliance}
                onSave={(val) => onUpdate(character.id, { brilliance: val })}
              />
              <EditableValue
                label="Senses"
                value={character.senses}
                onSave={(val) => onUpdate(character.id, { senses: val })}
              />
            </div>
            <div style={{ marginTop: '6px' }}>
              <EditableValue
                label="Presence"
                value={character.presence}
                onSave={(val) => onUpdate(character.id, { presence: val })}
              />
            </div>
          </div>

          {/* Section: Skills */}
          <div>
            <div className="section-label">Skills (Click value to edit)</div>
            <div className="stat-grid-4">
              <EditableValue
                label="Sharpstrike"
                value={character.sharpstrike}
                onSave={(val) => onUpdate(character.id, { sharpstrike: val })}
              />
              <EditableValue
                label="Ravage"
                value={character.ravage}
                onSave={(val) => onUpdate(character.id, { ravage: val })}
              />
              <EditableValue
                label="Melee"
                value={character.melee}
                onSave={(val) => onUpdate(character.id, { melee: val })}
              />
              <EditableValue
                label="Special"
                value={character.special}
                onSave={(val) => onUpdate(character.id, { special: val })}
              />
              <EditableValue
                label="Stealth"
                value={character.stealth}
                onSave={(val) => onUpdate(character.id, { stealth: val })}
              />
              <EditableValue
                label="Hardware"
                value={character.hardware}
                onSave={(val) => onUpdate(character.id, { hardware: val })}
              />
              <EditableValue
                label="Ordnance"
                value={character.ordnance}
                onSave={(val) => onUpdate(character.id, { ordnance: val })}
              />
              <EditableValue
                label="Medical"
                value={character.medical}
                onSave={(val) => onUpdate(character.id, { medical: val })}
              />
            </div>
          </div>

          {/* Section: Health & Bodyparts */}
          <div>
            <div className="section-label">Bodyparts & Total Health</div>
            <div className="stat-grid-3">
              <EditableValue
                label="Total HP"
                value={character.health}
                onSave={(val) => onUpdate(character.id, { health: val })}
                className={character.health <= 2 ? 'critical-border' : ''}
              />
              <EditableValue
                label="Head"
                value={character.head}
                onSave={(val) => onUpdate(character.id, { head: val })}
              />
              <EditableValue
                label="Torso"
                value={character.torso}
                onSave={(val) => onUpdate(character.id, { torso: val })}
              />
              <EditableValue
                label="R. Arm"
                value={character.right_arm}
                onSave={(val) => onUpdate(character.id, { right_arm: val })}
              />
              <EditableValue
                label="L. Arm"
                value={character.left_arm}
                onSave={(val) => onUpdate(character.id, { left_arm: val })}
              />
              <EditableValue
                label="R. Leg"
                value={character.right_leg}
                onSave={(val) => onUpdate(character.id, { right_leg: val })}
              />
            </div>
            <div style={{ marginTop: '6px' }}>
              <EditableValue
                label="L. Leg"
                value={character.left_leg}
                onSave={(val) => onUpdate(character.id, { left_leg: val })}
              />
            </div>
          </div>

          {/* Section: Stamina & Movement */}
          <div>
            <div className="section-label">Stamina & Vitals</div>
            <div className="stat-grid-3">
              <EditableValue
                label="Stamina"
                value={character.stamina}
                onSave={(val) => onUpdate(character.id, { stamina: val })}
              />
              <EditableValue
                label="Mental"
                value={character.mental}
                onSave={(val) => onUpdate(character.id, { mental: val })}
              />
              <EditableValue
                label="Move"
                value={character.movement_stat}
                onSave={(val) => onUpdate(character.id, { movement_stat: val })}
              />
            </div>
          </div>

          {/* Action Bar: Randomize traits with difficulty & Attack button */}
          <div className="card-actions-bar">
            <div className="difficulty-select-group">
              <span className="difficulty-label">Diff:</span>
              <select
                className="difficulty-select"
                value={difficulty}
                onChange={(e) => setDifficulty(parseInt(e.target.value, 10))}
              >
                <option value={1}>1</option>
                <option value={2}>2</option>
                <option value={3}>3</option>
                <option value={4}>4</option>
                <option value={5}>5</option>
              </select>
            </div>

            <button
              className="btn-action randomize-btn"
              onClick={handleRandomizeClick}
              title={`Randomize character traits (Difficulty ${difficulty})`}
            >
              <img
                src="/images/randomize.png"
                alt="Dice"
                style={{ width: '16px', height: '16px', objectFit: 'contain' }}
              />
              <span>Randomize</span>
            </button>

            <button
              className={`btn-action attack-btn ${!isCurrentTurn ? 'disabled' : ''}`}
              disabled={!isCurrentTurn}
              onClick={handleAttackClick}
              title={
                isCurrentTurn
                  ? 'Attack a target'
                  : "Attack is only available to the character whose turn it currently is"
              }
            >
              Attack {isCurrentTurn ? '' : '(Not Turn)'}
            </button>

            {onDeleteCharacter && !character.isNewDraft && (
              <button
                className="btn-delete-item"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteCharacter(character.id);
                }}
                title="Remove character"
              >
                <img
                  src="/images/delete.png"
                  alt="Delete"
                  style={{ width: '16px', height: '16px', objectFit: 'contain' }}
                />
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
