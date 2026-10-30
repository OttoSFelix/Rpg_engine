import React, { useState } from 'react';
import { CharacterData, ItemData } from '../types';

interface InventoryViewProps {
  character: CharacterData;
  onRandomizeInventory: (charId: number, difficulty: number) => void;
  onDeleteItem: (charId: number, itemId: string) => void;
  onReloadWeapon: (charId: number, itemId: string) => void;
  onEquipWeapon: (charId: number, itemId: string) => void;
  onDropItem: (charId: number, itemName: string) => void;
  onClose?: () => void;
}

export const InventoryView: React.FC<InventoryViewProps> = ({
  character,
  onRandomizeInventory,
  onDeleteItem,
  onReloadWeapon,
  onEquipWeapon,
  onDropItem,
  onClose,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [difficulty, setDifficulty] = useState<number>(3);

  const totalWeight = character.inventory.reduce((sum, item) => sum + (item.weight || 0), 0);
  const maxCapacity = (character.strength || 5) * 10;

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const itemName = e.dataTransfer.getData('text/plain');
    if (itemName) {
      onDropItem(character.id, itemName);
    }
  };

  return (
    <div className="sliding-inventory-panel">
      {/* Inventory Header */}
      <div className="inventory-header">
        <div className="inventory-title-group">
          <span className="inventory-title" title={`${character.name}'s Inventory`}>
            {character.name || 'Unit'}'s inv
          </span>
          <span className="inventory-sub">
            Weight: {totalWeight} / {maxCapacity}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <select
            className="difficulty-select"
            value={difficulty}
            onChange={(e) => setDifficulty(parseInt(e.target.value, 10))}
            title="Randomize Difficulty"
            style={{ fontSize: '0.75rem', background: '#0f1217', padding: '2px 4px', borderRadius: '4px' }}
          >
            <option value={1}>D1</option>
            <option value={2}>D2</option>
            <option value={3}>D3</option>
            <option value={4}>D4</option>
            <option value={5}>D5</option>
          </select>

          <button
            className="btn-action randomize-btn"
            style={{ padding: '4px 8px', fontSize: '0.72rem' }}
            onClick={() => onRandomizeInventory(character.id, difficulty)}
            title="Randomize inventory items"
          >
            <img
              src="/images/randomize.png"
              alt="Randomize"
              style={{ width: '14px', height: '14px', objectFit: 'contain' }}
            />
            <span>Random</span>
          </button>

          {onClose && (
            <button
              onClick={onClose}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#9aa4b2',
                cursor: 'pointer',
                fontSize: '1rem',
                padding: '0 4px',
              }}
              title="Close inventory"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Inventory Items List & Drop Target */}
      <div
        className="inventory-items-list"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {character.inventory.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#647082', padding: '20px 0', fontSize: '0.8rem' }}>
            Inventory is empty.
          </div>
        ) : (
          character.inventory.map((item) => {
            const isHeld = (character.held_weapon_id === item.item_id) || item.is_held || false;
            return (
              <div
                key={item.item_id || `${item.name}-${Math.random()}`}
                className={`inv-item-card ${isHeld ? 'held-weapon' : ''}`}
              >
                <div className="inv-item-top">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span className="inv-item-name">{item.name}</span>
                    {isHeld && <span className="held-weapon-badge">Held</span>}
                  </div>
                  <span className="inv-item-weight">{item.weight}</span>
                </div>

                <div className="inv-item-details">
                  <span>
                    {item.is_weapon ? (
                      <span className="ammo-badge">
                        Ammo: {item.magazine_bullets !== null ? item.magazine_bullets : '-'} /{' '}
                        {item.magazine_size !== null ? item.magazine_size : '-'}
                      </span>
                    ) : item.effect ? (
                      <span>
                        Effect:{' '}
                        {typeof item.effect === 'object' && item.effect !== null
                          ? Object.entries(item.effect)
                            .map(([k, v]) => `${k}: ${v}`)
                            .join(', ')
                          : String(item.effect)}
                      </span>
                    ) : (
                      <span>Type: {item.type}</span>
                    )}
                  </span>

                  <div className="inv-item-actions">
                    {item.is_weapon && (
                      <>
                        {isHeld ? (
                          <span className="btn-equipped" title="Currently equipped as held weapon">
                            Equipped
                          </span>
                        ) : (
                          <button
                            className="btn-equip"
                            onClick={() => onEquipWeapon(character.id, item.item_id)}
                            title={`Equip ${item.name} as held weapon`}
                          >
                            Equip
                          </button>
                        )}

                        <button
                          className="btn-reload"
                          onClick={() => onReloadWeapon(character.id, item.item_id)}
                          title={`Reload weapon (${item.magazine_bullets}/${item.magazine_size})`}
                        >
                          Reload
                        </button>
                      </>
                    )}

                    <button
                      className="btn-delete-item"
                      onClick={() => onDeleteItem(character.id, item.item_id)}
                      title={`Delete ${item.name} from inventory`}
                    >
                      <img
                        src="/images/delete.png"
                        alt="Delete"
                        style={{ width: '16px', height: '16px', objectFit: 'contain' }}
                      />
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        )}

        {/* Drag and Drop notice */}
        <div className={`inventory-drop-zone ${isDragOver ? 'drag-over' : ''}`}>
          Drop items here from the vault
        </div>
      </div>
    </div>
  );
};
