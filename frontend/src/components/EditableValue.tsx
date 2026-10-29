import React, { useState, useEffect, useRef } from 'react';

interface EditableValueProps {
  label: string;
  value: number;
  onSave: (val: number) => void;
  min?: number;
  max?: number;
  className?: string;
}

export const EditableValue: React.FC<EditableValueProps> = ({
  label,
  value,
  onSave,
  min = 0,
  max = 99,
  className = '',
}) => {
  const safeVal = value ?? 0;
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState(safeVal.toString());
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setDraft((value ?? 0).toString());
  }, [value]);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleCommit = () => {
    setIsEditing(false);
    const parsed = parseInt(draft, 10);
    if (!isNaN(parsed) && parsed !== value) {
      const clamped = Math.max(min, Math.min(max, parsed));
      onSave(clamped);
    } else {
      setDraft((value ?? 0).toString());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleCommit();
    } else if (e.key === 'Escape') {
      setIsEditing(false);
      setDraft((value ?? 0).toString());
    }
  };

  return (
    <div
      className={`stat-box ${className}`}
      onClick={(e) => {
        e.stopPropagation();
        setIsEditing(true);
      }}
      title={`Click to edit ${label}`}
    >
      <span className="stat-title">{label}</span>
      {isEditing ? (
        <input
          ref={inputRef}
          type="number"
          className="stat-input"
          value={draft}
          min={min}
          max={max}
          onChange={(e) => setDraft(e.target.value)}
          onBlur={handleCommit}
          onKeyDown={handleKeyDown}
          onClick={(e) => e.stopPropagation()}
        />
      ) : (
        <span className="stat-val">{value}</span>
      )}
    </div>
  );
};
