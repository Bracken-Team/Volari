from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

vollog = logging.getLogger(__name__)


class TimelineEvent:
    """Represents a single event in the timeline."""
    
    def __init__(self, timestamp: datetime, event_type: str, description: str, details: Dict[str, Any] = None):
        """
        Initialize a timeline event.
        
        Args:
            timestamp: When the event occurred
            event_type: Type of event (process, network, file, registry)
            description: Human-readable description
            details: Additional event details
        """
        self.timestamp = timestamp
        self.event_type = event_type
        self.description = description
        self.details = details or {}
        
    def __repr__(self):
        return f"TimelineEvent({self.timestamp}, {self.event_type}, {self.description})"
        
    def to_dict(self):
        """Convert to dictionary for display."""
        return {
            'Timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else 'Unknown',
            'Type': self.event_type,
            'Description': self.description,
            **self.details
        }


class TimelineAggregator:
    """Aggregates events from multiple sources into a unified timeline."""
    
    def __init__(self):
        self.events: List[TimelineEvent] = []
        
    def add_process_events(self, process_data: List[Dict[str, Any]]):
        """
        Extract timeline events from process data.
        
        Args:
            process_data: List of process dictionaries from pslist/psscan
        """
        if not process_data:
            return
        
        vollog.info(f"Processing {len(process_data)} process entries for timeline")
        parsed_count = 0
            
        for proc in process_data:
            # Process creation time
            create_time = proc.get('CreateTime')
            if create_time and create_time != 'N/A':
                try:
                    # Parse the timestamp
                    timestamp = self._parse_timestamp(create_time)
                    if timestamp:
                        parsed_count += 1
                        description = f"Process created: {proc.get('ImageFileName', 'Unknown')} (PID: {proc.get('PID', 'N/A')})"
                        event = TimelineEvent(
                            timestamp=timestamp,
                            event_type='Process',
                            description=description,
                            details={
                                'PID': proc.get('PID', 'N/A'),
                                'PPID': proc.get('PPID', 'N/A'),
                                'Process': proc.get('ImageFileName', 'Unknown')
                            }
                        )
                        self.events.append(event)
                except Exception as e:
                    vollog.debug(f"Error parsing process timestamp: {e}")
                    
            # Process exit time
            exit_time = proc.get('ExitTime')
            if exit_time and exit_time != 'N/A' and exit_time != '':
                try:
                    timestamp = self._parse_timestamp(exit_time)
                    if timestamp:
                        parsed_count += 1
                        description = f"Process exited: {proc.get('ImageFileName', 'Unknown')} (PID: {proc.get('PID', 'N/A')})"
                        event = TimelineEvent(
                            timestamp=timestamp,
                            event_type='Process',
                            description=description,
                            details={
                                'PID': proc.get('PID', 'N/A'),
                                'Process': proc.get('ImageFileName', 'Unknown')
                            }
                        )
                        self.events.append(event)
                except Exception as e:
                    vollog.debug(f"Error parsing exit timestamp: {e}")
        
        vollog.info(f"Successfully parsed {parsed_count} process timeline events")
                    
    def add_network_events(self, network_data: List[Dict[str, Any]]):
        """
        Extract timeline events from network connection data.
        
        Args:
            network_data: List of network connection dictionaries
        """
        if not network_data:
            return
            
        for conn in network_data:
            # Network connections often don't have explicit timestamps
            # We can use the Created field if available
            created = conn.get('Created')
            if created and created != 'N/A':
                try:
                    timestamp = self._parse_timestamp(created)
                    if timestamp:
                        local = f"{conn.get('LocalAddr', '')}:{conn.get('LocalPort', '')}"
                        foreign = f"{conn.get('ForeignAddr', '')}:{conn.get('ForeignPort', '')}"
                        description = f"Network connection: {local} -> {foreign} ({conn.get('State', 'Unknown')})"
                        event = TimelineEvent(
                            timestamp=timestamp,
                            event_type='Network',
                            description=description,
                            details={
                                'Protocol': conn.get('Proto', 'N/A'),
                                'Local': local,
                                'Foreign': foreign,
                                'State': conn.get('State', 'Unknown'),
                                'PID': conn.get('PID', 'N/A')
                            }
                        )
                        self.events.append(event)
                except Exception as e:
                    vollog.debug(f"Error parsing network timestamp: {e}")
                    
    def add_file_events(self, file_data: List[Dict[str, Any]]):
        """
        Extract timeline events from file data.
        
        Args:
            file_data: List of file dictionaries from filescan
        """
        if not file_data:
            return
            
        # File scan typically doesn't have timestamps, but we can note file presence
        # For now, we'll skip file events unless they have timestamp data
        for file_entry in file_data:
            # Check for any timestamp fields
            for field in ['Created', 'Modified', 'Accessed']:
                timestamp_str = file_entry.get(field)
                if timestamp_str and timestamp_str != 'N/A':
                    try:
                        timestamp = self._parse_timestamp(timestamp_str)
                        if timestamp:
                            description = f"File {field.lower()}: {file_entry.get('Name', 'Unknown')}"
                            event = TimelineEvent(
                                timestamp=timestamp,
                                event_type='File',
                                description=description,
                                details={
                                    'Name': file_entry.get('Name', 'Unknown'),
                                    'Offset': file_entry.get('Offset', 'N/A')
                                }
                            )
                            self.events.append(event)
                    except Exception as e:
                        vollog.debug(f"Error parsing file timestamp: {e}")
                        
    def add_registry_events(self, registry_data: List[Dict[str, Any]]):
        """
        Extract timeline events from registry data.
        
        Args:
            registry_data: List of registry hive dictionaries
        """
        if not registry_data:
            return
            
        # Registry hives may have LastWritten timestamps
        for hive in registry_data:
            last_written = hive.get('LastWritten')
            if last_written and last_written != 'N/A':
                try:
                    timestamp = self._parse_timestamp(last_written)
                    if timestamp:
                        description = f"Registry hive modified: {hive.get('Name', 'Unknown')}"
                        event = TimelineEvent(
                            timestamp=timestamp,
                            event_type='Registry',
                            description=description,
                            details={
                                'Hive': hive.get('Name', 'Unknown'),
                                'Offset': hive.get('Offset', 'N/A')
                            }
                        )
                        self.events.append(event)
                except Exception as e:
                    vollog.debug(f"Error parsing registry timestamp: {e}")
                    
    def get_sorted_events(self) -> List[TimelineEvent]:
        """Get all events sorted by timestamp."""
        # Filter out events without valid timestamps
        valid_events = [e for e in self.events if e.timestamp is not None]
        return sorted(valid_events, key=lambda x: x.timestamp)
        
    def get_events_by_type(self, event_type: str) -> List[TimelineEvent]:
        """Get events filtered by type."""
        return [e for e in self.get_sorted_events() if e.event_type == event_type]
        
    def get_events_in_range(self, start: datetime, end: datetime) -> List[TimelineEvent]:
        """Get events within a time range."""
        return [e for e in self.get_sorted_events() 
                if e.timestamp and start <= e.timestamp <= end]
                
    def clear(self):
        """Clear all events."""
        self.events.clear()
        
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """
        Parse a timestamp string into a datetime object.
        
        Args:
            timestamp_str: String representation of timestamp
            
        Returns:
            datetime object or None if parsing fails
        """
        if not timestamp_str or timestamp_str == 'N/A' or timestamp_str.strip() == '':
            return None
            
        # Clean the string
        clean_str = timestamp_str.strip()
        
        # Try common formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S UTC',
            '%Y-%m-%d %H:%M:%S.%f UTC',
            '%m/%d/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                # Remove UTC suffix if present for parsing
                test_str = clean_str.replace(' UTC', '').replace(' +0000', '').strip()
                return datetime.strptime(test_str, fmt.replace(' UTC', ''))
            except ValueError:
                continue
        
        # Try ISO 8601 format with timezone (e.g., '2025-10-27 16:58:04+00:00')
        try:
            # Remove timezone info for parsing (Python's strptime doesn't handle +00:00 well)
            if '+' in clean_str or clean_str.endswith('Z'):
                # Remove timezone offset
                clean_str = clean_str.replace('Z', '').split('+')[0].split('-')
                # Rejoin in case the date had dashes
                if len(clean_str) > 3:
                    clean_str = '-'.join(clean_str[:3]) + ' ' + clean_str[3] if len(clean_str) > 3 else '-'.join(clean_str)
                else:
                    clean_str = timestamp_str.split('+')[0].strip()
                return datetime.strptime(clean_str, '%Y-%m-%d %H:%M:%S')
        except Exception:
            pass
        
        # Log the first few failed timestamps for debugging
        if len(self.events) < 5:  # Only log first few to avoid spam
            vollog.warning(f"Could not parse timestamp format: '{timestamp_str}'")
        return None
