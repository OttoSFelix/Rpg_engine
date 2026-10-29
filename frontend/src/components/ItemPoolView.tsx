import React from 'react';
import { ItemData } from '../types';

interface ItemPoolViewProps {
  items: ItemData[];
  selectedCharacterName?: string;
  onAddItemToSelected?: (itemName: string) => void;
}

export const ItemPoolView: React.FC<ItemPoolViewProps> = ({
  items,
  selectedCharacterName,
  onAddItemToSelected,
}) => {
  const handleDragStart = (e: React.DragEvent, itemName: string) => {
    e.dataTransfer.setData('text/plain', itemName);
    e.dataTransfer.effectAllowed = 'copy';
  };

  return (
    <div className="item-pool-panel">
      <div className="item-pool-header">
        <span className="item-pool-title">The vault</span>
        <span style={{ fontSize: '0.75rem', color: '#9aa4b2' }}>
          Drag items to character inventory
        </span>
      </div>

      <div className="item-pool-grid">
        {items.map((item) => (
          <div
            key={item.name}
            className="pool-item-card"
            draggable
            onDragStart={(e) => handleDragStart(e, item.name)}
            title={`Drag ${item.name} into character inventory`}
          >
            <div className="pool-item-top">
              <span className="pool-item-name">{item.name}</span>
              <span className="pool-item-type">
                {item.is_weapon ? item.type : item.effect ? 'Stim' : 'Item'}
              </span>
            </div>

            <div className="pool-item-stats">
              <span>Weight: {item.weight}</span>
              {item.is_weapon && (
                <>
                  <span>
                    Dmg: {item.damage} ({item.damage_type})
                  </span>
                  <span>Mag: {item.magazine_size} bullets</span>
                </>
              )}
              {item.effect && (
                <span>
                  Effect:{' '}
                  {typeof item.effect === 'object' && item.effect !== null
                    ? Object.entries(item.effect)
                      .map(([k, v]) => `${k}: ${v}`)
                      .join(', ')
                    : String(item.effect)}
                </span>
              )}
            </div>

            {onAddItemToSelected && selectedCharacterName && (
              <button
                className="btn-action"
                style={{
                  marginTop: '4px',
                  padding: '3px 6px',
                  fontSize: '0.7rem',
                  justifyContent: 'center',
                }}
                onClick={() => onAddItemToSelected(item.name)}
                title={`Add directly to ${selectedCharacterName}`}
              >
                + Add to {selectedCharacterName}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
